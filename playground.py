from url_ranking_model import UrlRanker
from scraper import scrape_links

"""
Quick script to see how the scraper is working
"""


def preprocess_urls(url_data, base_url="https://www.a2gov.org"):
    """
    Cleans and processes URL list:
    - Skips URLs starting with "#"
    - Converts relative URLs ("/path") into full URLs using base URL
    """
    cleaned_urls = []
    cleaned_anchor_texts = []

    for url, anchor_text in url_data:
        if url.startswith("#"):  # Skip fragment links
            continue
        if url.startswith("/"):  # Convert relative URLs to absolute
            url = base_url + url

        cleaned_urls.append(url)
        cleaned_anchor_texts.append(anchor_text)

    return cleaned_urls, cleaned_anchor_texts


if __name__ == "__main__":
    ranker = UrlRanker()

    url = "https://www.a2gov.org/finance-and-administrative-services/purchasing/bid-process"

    url_data = scrape_links(url)
    # print(extracted_data)

    urls, anchor_texts = preprocess_urls(url_data, url)

    # Call rank_urls with the extracted lists
    ranked_results = ranker.rank_urls(urls, anchor_texts)

    print(ranked_results)
