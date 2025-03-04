from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_graphql import GraphQLView
import graphene
import re
from scraper import scrape_links, preprocess_urls, is_valid_url
from url_ranking_model import UrlRanker
from database import (
    init_db,
    save_links,
    get_top_links,
    get_links_from_domain,
    get_document_links,
    search_links_by_keyword,
    get_avg_score_per_domain,
)
import pandas as pd
from config import HIGH_SCORE_THRESHOLD

app = Flask(__name__)

# Init duck database
init_db()

# Load ML model
ranker = UrlRanker("model.pkl")

# Swagger setup
SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "URL Scraper API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route("/static/swagger.json")
def swagger_json():
    """
    Returns documentation.
    """
    return jsonify(
        {
            "swagger": "2.0",
            "info": {
                "title": "URL Scraper API",
                "description": "API for scraping and ranking URLs",
                "version": "1.0",
            },
            "paths": {
                "/scrape": {
                    "get": {
                        "summary": "Scrape a webpage and rank links",
                        "parameters": [
                            {
                                "name": "url",
                                "in": "query",
                                "required": True,
                                "type": "string",
                            }
                        ],
                        "responses": {
                            "200": {"description": "Scraped and ranked links"},
                            "400": {"description": "Invalid request"},
                            "404": {"description": "No links found"},
                        },
                    }
                },
                "/top-links": {
                    "get": {
                        "summary": "Retrieve top-ranked links, optionally filtered by domain",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "type": "integer",
                                "default": 10,
                            },
                            {
                                "name": "domain",
                                "in": "query",
                                "type": "string",
                                "required": False,
                            },
                        ],
                        "responses": {
                            "200": {"description": "Top links retrieved"},
                            "400": {"description": "Invalid request"},
                        },
                    }
                },
                "/links-from-domain": {
                    "get": {
                        "summary": "Retrieve links from a specific domain",
                        "parameters": [
                            {
                                "name": "domain",
                                "in": "query",
                                "required": True,
                                "type": "string",
                            }
                        ],
                        "responses": {
                            "200": {"description": "Links from domain retrieved"},
                            "400": {"description": "Missing domain parameter"},
                        },
                    }
                },
                "/document-links": {
                    "get": {
                        "summary": "Retrieve only document links (PDFs, Excel, Word)",
                        "responses": {
                            "200": {"description": "Document links retrieved"}
                        },
                    }
                },
                "/search-links": {
                    "get": {
                        "summary": "Search for links by keyword in anchor text",
                        "parameters": [
                            {
                                "name": "keyword",
                                "in": "query",
                                "required": True,
                                "type": "string",
                            }
                        ],
                        "responses": {
                            "200": {"description": "Search results for links"},
                            "400": {"description": "Missing keyword parameter"},
                        },
                    }
                },
                "/avg-score-per-domain": {
                    "get": {
                        "summary": "Retrieve the average relevance score per domain",
                        "responses": {
                            "200": {
                                "description": "Average scores per domain retrieved"
                            }
                        },
                    }
                },
                "/graphql": {
                    "post": {
                        "summary": "Execute GraphQL queries",
                        "description": "Send GraphQL queries in the request body.",
                        "parameters": [
                            {
                                "name": "query",
                                "in": "body",
                                "required": True,
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "example": "{ topLinks(limit: 5) { url anchorText score } }",
                                        }
                                    },
                                },
                            }
                        ],
                        "responses": {
                            "200": {"description": "GraphQL response"},
                            "400": {"description": "Invalid request"},
                        },
                    }
                },
            },
        }
    )


# REST endpoints
@app.route("/scrape", methods=["GET"])
def scrape():
    """
    Scrape a webpage, rank links, and scrape high-value non-file URLs by one more level.
    """
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    # Perform first scrape
    links = scrape_links(url)
    if not links:
        return jsonify({"error": "No links found"}), 404

    urls, anchor_texts = preprocess_urls(links, url)
    ranked_df = ranker.rank_urls(urls, anchor_texts)
    # Track source page
    ranked_df["scraped_from"] = url

    # Function to check if URL ends with a file extension
    def is_file_link(link):
        return bool(
            re.search(r"\.[a-zA-Z0-9]{2,5}$", link)
        )  # Matches URLs ending in ".ext"

    # Extract only high-value URLs that are not files
    # Ranking threshold defined in config
    high_value_urls = ranked_df[
        (ranked_df["score"] > HIGH_SCORE_THRESHOLD)
        & (~ranked_df["url"].apply(is_file_link))
    ]

    # print("HIGH VALUE LINKES")
    # print(high_value_urls)

    # List to store second-level data
    second_level_data = []

    # Scrape one more level on high-value non-file links
    for new_url in high_value_urls["url"]:
        print(f"Deep scraping: {new_url}")

        if not is_valid_url(new_url):
            print(f"Skipping deep scrape invalid URL: {url}")
            continue

        second_level_links = scrape_links(new_url)

        if second_level_links:
            second_urls, second_anchor_texts = preprocess_urls(
                second_level_links, new_url
            )
            second_ranked_df = ranker.rank_urls(second_urls, second_anchor_texts)
            second_ranked_df["scraped_from"] = new_url

            # Collect second-level data
            second_level_data.append(second_ranked_df)

    print(second_level_data)

    # If any second-level data exists, append it to the main dataframe
    if second_level_data:
        ranked_df = pd.concat([ranked_df] + second_level_data, ignore_index=True)

    ranked_df = (
        ranked_df.drop_duplicates(subset=["url"])
        .sort_values(by="score", ascending=False)
        .reset_index(drop=True)
    )

    # Save results to DuckDB
    save_links(ranked_df)

    return jsonify(
        {
            "message": f"Scraped {len(ranked_df)} links from {url} (including second-level scrapes)",
            "ranked_links": ranked_df.to_dict(orient="records"),
        }
    )


@app.route("/top-links", methods=["GET"])
def top_links():
    """Retrieve top-ranked links, optionally filtered by domain."""
    limit = int(request.args.get("limit", 10))
    domain = request.args.get("domain")

    results = get_top_links(limit, domain) if domain else get_top_links(limit)

    return jsonify({"top_links": results})


@app.route("/links-from-domain", methods=["GET"])
def links_from_domain():
    """Retrieve links from a specific domain."""
    domain = request.args.get("domain")
    if not domain:
        return jsonify({"error": "Domain parameter is required"}), 400
    results = get_links_from_domain(domain)
    return jsonify({"links_from_domain": results})


@app.route("/document-links", methods=["GET"])
def document_links():
    """Retrieve only document links (PDFs, Excel, Word)."""
    results = get_document_links()
    return jsonify({"document_links": results})


@app.route("/search-links", methods=["GET"])
def search_links():
    """Search for links by keyword in anchor text."""
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400
    results = search_links_by_keyword(keyword)
    return jsonify({"search_results": results})


@app.route("/avg-score-per-domain", methods=["GET"])
def avg_score_per_domain():
    """Retrieve the average relevance score per domain."""
    results = get_avg_score_per_domain()
    return jsonify({"avg_scores": results})


# --- GraphQL Schema ---
class LinkType(graphene.ObjectType):
    url = graphene.String()
    anchor_text = graphene.String()
    score = graphene.Float()
    scraped_from = graphene.String()
    domain = graphene.String()


class AvgScorePerDomainType(graphene.ObjectType):
    domain = graphene.String()
    avg_score = graphene.Float()


class Query(graphene.ObjectType):
    top_links = graphene.List(LinkType, limit=graphene.Int(default_value=10))
    links_from_domain = graphene.List(LinkType, domain=graphene.String(required=True))
    document_links = graphene.List(LinkType)
    search_links = graphene.List(LinkType, keyword=graphene.String(required=True))
    avg_score_per_domain = graphene.List(AvgScorePerDomainType)

    def resolve_top_links(self, info, limit):
        results = get_top_links(limit)
        return [LinkType(**result) for result in results]

    def resolve_links_from_domain(self, info, domain):
        results = get_links_from_domain(domain)
        return [LinkType(**l) for l in results]

    def resolve_document_links(self, info):
        results = get_document_links()
        return [LinkType(**l) for l in results]

    def resolve_search_links(self, info, keyword):
        results = search_links_by_keyword(keyword)
        return [LinkType(**l) for l in results]

    def resolve_avg_score_per_domain(self, info):
        results = get_avg_score_per_domain()
        return [AvgScorePerDomainType(**l) for l in results]


schema = graphene.Schema(query=Query)
app.add_url_rule(
    "/graphql", view_func=GraphQLView.as_view("graphql", schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run(debug=True)
