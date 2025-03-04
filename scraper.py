import re

from playwright.sync_api import sync_playwright, TimeoutError, Error
from urllib.parse import urljoin


def is_valid_url(link):
    """
    Check if the URL is valid and not JavaScript-based.
    """
    # Filtering out links that can't be scraped
    if not link or link.strip() in [
        "#",
        "javascript:void(0)",
        "javascript",
        "javascript:void(0);",
    ]:
        return False

    return link


def normalize_url(link, base_url):
    """
    Cleans and normalizes URLs by:
    - Resolving relative URLs correctly.
    - Removing duplicate path segments.
    - Fixing double slashes.
    """
    # Convert relative URLs to absolute
    normalized = urljoin(base_url, link)

    # Remove duplicate slashes (except after "http://")
    normalized = re.sub(r"(?<!:)//+", "/", normalized)

    # Remove trailing slash (optional, unless needed)
    normalized = normalized.rstrip("/")

    return normalized


def scrape_links(url):
    """
    Scrape links and anchor text from a given URL using Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=10000)  # 10-second timeout
        except TimeoutError or Error:
            print(f"Timeout occurred for {url}, skipping...")
            browser.close()
            return []  # Return empty list to avoid breaking the loop

        # Extract all <a> tags with href attributes
        links = page.query_selector_all("a")

        # Could have flag to enable better swapping here
        if not links:  # If no links found, try Firefox
            print("No links found with Chromium. Trying Firefox...")

            browser.close()  # Close the Chromium browser

            # Try Firefox headless
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=10000)
            except TimeoutError or Error:
                print(f"Timeout occurred for {url}, skipping...")
                browser.close()
                return []

            links = page.query_selector_all("a")

        extracted_data = []

        for link in links:
            href = link.get_attribute("href")
            anchor_text = link.inner_text().strip()
            if href and anchor_text:
                extracted_data.append((href, anchor_text))

        browser.close()
        return extracted_data


def preprocess_urls(url_data, base_url):
    """
    Cleans and processes URL list:
    - Skips invalid URLs (e.g., JavaScript links, fragments)
    - Resolves relative URLs correctly
    - Fixes malformed duplicate slashes
    """
    cleaned_urls = []
    cleaned_anchor_texts = []

    print("Processing URLs!")

    for url, anchor_text in url_data:
        # Skip invalid URLs before processing
        if not is_valid_url(url):
            # For debugging
            # print(f"Skipping invalid URL: {url}")
            continue

        url = normalize_url(url, base_url)

        cleaned_urls.append(url)
        cleaned_anchor_texts.append(anchor_text)

    return cleaned_urls, cleaned_anchor_texts
