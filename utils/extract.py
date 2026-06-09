import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Any, Dict, List, Optional


BASE_URL = "https://fashion-studio.dicoding.dev"
MAX_RETRIES = 3
REQUEST_TIMEOUT = 10

logger = logging.getLogger(__name__)


def get_page_url(page_number: int) -> str:
    if not isinstance(page_number, int) or page_number < 1:
        raise ValueError("page_number must be a positive integer.")

    if page_number == 1:
        return BASE_URL + "/"

    return f"{BASE_URL}/page{page_number}"


def extract_price(card: Any) -> Optional[str]:
    span_price = card.select_one(".price-container span.price")
    if span_price:
        return span_price.get_text(strip=True)

    p_price = card.find("p", class_="price")
    if p_price:
        return p_price.get_text(strip=True)

    return None


def parse_product_card(card: Any, timestamp: str) -> Dict[str, Optional[str]]:
    title_tag = card.find("h3", class_="product-title")
    title = title_tag.get_text(strip=True) if title_tag else None

    price = extract_price(card)

    rating = None
    colors = None
    size = None
    gender = None

    for p in card.find_all("p"):
        text = p.get_text(strip=True)

        if text.startswith("Rating:"):
            rating = text.replace("Rating:", "").strip()
        elif "Colors" in text:
            colors = text
        elif text.startswith("Size:"):
            size = text
        elif text.startswith("Gender:"):
            gender = text

    return {
        "Title": title,
        "Price": price,
        "Rating": rating,
        "Colors": colors,
        "Size": size,
        "Gender": gender,
        "timestamp": timestamp,
    }


def scrape_page(
    session: requests.Session, url: str
) -> List[Dict[str, Optional[str]]]:
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            break
        except requests.exceptions.Timeout:
            last_error = requests.exceptions.Timeout(
                f"Request timed out for URL: {url}"
            )
        except requests.exceptions.ConnectionError:
            last_error = requests.exceptions.ConnectionError(
                f"Failed to connect to URL: {url}"
            )
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(
                f"HTTP error for URL {url}: {e}"
            ) from e

        if attempt == MAX_RETRIES:
            raise last_error

        logger.warning("Retrying %s (%s/%s)...", url, attempt, MAX_RETRIES)

    soup = BeautifulSoup(response.text, "html.parser")
    product_cards = soup.find_all("div", class_="collection-card")

    products = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for card in product_cards:
        try:
            product = parse_product_card(card, timestamp)
            products.append(product)
        except Exception as e:
            logger.warning("Failed to parse a product card: %s", e)
        continue

    return products


def scrape_all_pages(total_pages: int = 50) -> List[Dict[str, Optional[str]]]:
    if not isinstance(total_pages, int) or total_pages < 1:
        raise ValueError("total_pages must be a positive integer.")

    session = requests.Session()
    all_products = []

    for page_number in range(1, total_pages + 1):
        url = get_page_url(page_number)
        try:
            logger.info(
                "Scraping page %s/%s: %s", page_number, total_pages, url
            )
            products = scrape_page(session, url)
            all_products.extend(products)
        except Exception as e:
            logger.error("Error scraping page %s: %s", page_number, e)
            continue

    logger.info("Total raw data collected: %s products", len(all_products))
    return all_products
