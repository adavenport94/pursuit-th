import duckdb
import pandas as pd
import re

from config import DB_FILE
from contextlib import contextmanager


@contextmanager
def get_db_connection():
    """
    Help with managaging DuckDB connections.
    """
    conn = duckdb.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Init DuckDB and set up main table with indexing.
    """
    with get_db_connection() as conn:
        # Create the main 'links' table with domain included
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                url TEXT,
                anchor_text TEXT,
                score DOUBLE,
                scraped_from TEXT,
                domain TEXT
            )
        """
        )

        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_url ON links(url)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_scraped_from ON links(scraped_from)"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_anchor_text ON links(anchor_text)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_domain ON links(domain)")

    print("Database initialized with optimized indexing.")

def extract_domain(url):
    """
    Extracts the domain from a given URL.
    """
    domain = re.search(r"https?://([^/]+)", url)
    return domain.group(1) if domain else ""

def save_links(df):
    """
    Save ranked links to db, adding domain column.
    """
    df["domain"] = df["scraped_from"].apply(extract_domain)

    with get_db_connection() as conn:
        df.to_sql("links", conn, if_exists="append", index=False)

    print(f"Saved {len(df)} links to database.")


def get_top_links(limit=10, domain=None):
    """
    Fetch top-ranked links, can filter by domain.
    """
    with get_db_connection() as conn:
        if domain:
            query = f"""
                SELECT * 
                FROM links 
                WHERE domain = '{domain}'
                ORDER BY score DESC 
                LIMIT {limit}
            """
        else:
            query = f"""
                SELECT * 
                FROM links 
                ORDER BY score DESC 
                LIMIT {limit}
            """
        df = conn.execute(query).fetchdf()
    return df.to_dict(orient="records")


def get_links_from_domain(domain):
    """
    Fetch all links from a specific domain.
    """
    with get_db_connection() as conn:
        df = conn.execute("SELECT * FROM links WHERE domain = ?", (domain,)).fetchdf()
    return df.to_dict(orient="records")


def get_document_links():
    """
    Fetch only document links.
    """
    with get_db_connection() as conn:
        query = """
            SELECT * FROM links 
            WHERE url LIKE '%.pdf' 
               OR url LIKE '%.xls' 
               OR url LIKE '%.xlsx' 
               OR url LIKE '%.doc' 
               OR url LIKE '%.docx'
        """
        df = conn.execute(query).fetchdf()
    return df.to_dict(orient="records")


def search_links_by_keyword(keyword):
    """
    Search for links by keyword by anchor text.
    """
    with get_db_connection() as conn:
        query = f"""
        SELECT * FROM links 
        WHERE anchor_text LIKE '%{keyword}%'
        """
        df = conn.execute(query).fetchdf()
    return df.to_dict(orient="records")


def get_avg_score_per_domain():
    """
    Fetch the average relevance score per domain
    ."""
    with get_db_connection() as conn:
        query = """
            SELECT domain, AVG(score) AS avg_score 
            FROM links 
            GROUP BY domain
        """
        df = conn.execute(query).fetchdf()

    # Convert the dataframe to a list of dictionaries
    result = df.to_dict(orient="records")

    # print("Processed Result:", result)

    return result
