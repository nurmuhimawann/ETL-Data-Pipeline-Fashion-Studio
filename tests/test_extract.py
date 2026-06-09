import pytest
import requests
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from utils.extract import (
    get_page_url,
    extract_price,
    parse_product_card,
    scrape_page,
    scrape_all_pages,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_HTML = """
<html><body>
  <div class="collection-card">
    <div class="product-details">
      <h3 class="product-title">T-shirt 1</h3>
      <div class="price-container"><span class="price">$100.00</span></div>
      <p>Rating: ⭐ 4.5 / 5</p>
      <p>3 Colors</p>
      <p>Size: M</p>
      <p>Gender: Men</p>
    </div>
  </div>
  <div class="collection-card">
    <div class="product-details">
      <h3 class="product-title">Pants 2</h3>
      <div class="price-container"><span class="price">$200.00</span></div>
      <p>Rating: ⭐ 3.8 / 5</p>
      <p>5 Colors</p>
      <p>Size: L</p>
      <p>Gender: Women</p>
    </div>
  </div>
</body></html>
"""

SAMPLE_HTML_UNAVAILABLE = """
<html><body>
  <div class="collection-card">
    <div class="product-details">
      <h3 class="product-title">Unknown Product</h3>
      <p class="price">Price Unavailable</p>
      <p>Rating: ⭐ Invalid Rating / 5</p>
      <p>5 Colors</p>
      <p>Size: M</p>
      <p>Gender: Men</p>
    </div>
  </div>
</body></html>
"""


def make_mock_response(html, status_code=200):
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.text = html
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def make_card(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.find("div", class_="collection-card")


# ── get_page_url ─────────────────────────────────────────────────────────────

class TestGetPageUrl:
    def test_page_1_returns_base_url(self):
        url = get_page_url(1)
        assert url == "https://fashion-studio.dicoding.dev/"

    def test_page_2_returns_page2(self):
        url = get_page_url(2)
        assert url == "https://fashion-studio.dicoding.dev/page2"

    def test_page_50_returns_page50(self):
        url = get_page_url(50)
        assert url == "https://fashion-studio.dicoding.dev/page50"

    def test_get_page_url_raises_for_zero_page(self):
        with pytest.raises(ValueError):
            get_page_url(0)

    def test_get_page_url_raises_for_negative_page(self):
        with pytest.raises(ValueError):
            get_page_url(-1)

    def test_get_page_url_raises_for_non_integer_page(self):
        with pytest.raises(ValueError):
            get_page_url("2")


# ── extract_price ────────────────────────────────────────────────────────────

class TestExtractPrice:
    def test_extracts_span_price(self):
        card = make_card(SAMPLE_HTML)

        price = extract_price(card)

        assert price == "$100.00"

    def test_extracts_unavailable_price_from_p_tag(self):
        card = make_card(SAMPLE_HTML_UNAVAILABLE)

        price = extract_price(card)

        assert price == "Price Unavailable"

    def test_returns_none_when_price_not_found(self):
        html = """
        <html><body>
          <div class="collection-card">
            <h3 class="product-title">No Price Product</h3>
          </div>
        </body></html>
        """
        card = make_card(html)

        price = extract_price(card)

        assert price is None


# ── parse_product_card ───────────────────────────────────────────────────────

class TestParseProductCard:
    def test_parse_product_card_returns_correct_product_dict(self):
        card = make_card(SAMPLE_HTML)
        timestamp = "2024-01-01 00:00:00"

        product = parse_product_card(card, timestamp)

        assert product["Title"] == "T-shirt 1"
        assert product["Price"] == "$100.00"
        assert "4.5" in product["Rating"]
        assert product["Colors"] == "3 Colors"
        assert product["Size"] == "Size: M"
        assert product["Gender"] == "Gender: Men"
        assert product["timestamp"] == timestamp

    def test_parse_product_card_handles_unavailable_product(self):
        card = make_card(SAMPLE_HTML_UNAVAILABLE)
        timestamp = "2024-01-01 00:00:00"

        product = parse_product_card(card, timestamp)

        assert product["Title"] == "Unknown Product"
        assert product["Price"] == "Price Unavailable"
        assert "Invalid Rating" in product["Rating"]
        assert product["Colors"] == "5 Colors"
        assert product["Size"] == "Size: M"
        assert product["Gender"] == "Gender: Men"
        assert product["timestamp"] == timestamp


# ── scrape_page ──────────────────────────────────────────────────────────────

class TestScrapePage:
    def test_scrape_returns_correct_fields(self):
        session = MagicMock()
        session.get.return_value = make_mock_response(SAMPLE_HTML)

        products = scrape_page(session, "https://fashion-studio.dicoding.dev/")

        assert len(products) == 2
        assert products[0]["Title"] == "T-shirt 1"
        assert products[0]["Price"] == "$100.00"
        assert "4.5" in products[0]["Rating"]
        assert products[0]["Colors"] == "3 Colors"
        assert products[0]["Size"] == "Size: M"
        assert products[0]["Gender"] == "Gender: Men"
        assert "timestamp" in products[0]

    def test_scrape_price_unavailable(self):
        session = MagicMock()
        session.get.return_value = make_mock_response(SAMPLE_HTML_UNAVAILABLE)

        products = scrape_page(session, "https://fashion-studio.dicoding.dev/")

        assert len(products) == 1
        assert products[0]["Price"] == "Price Unavailable"

    def test_scrape_raises_timeout(self):
        session = MagicMock()
        session.get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(requests.exceptions.Timeout):
            scrape_page(session, "https://fashion-studio.dicoding.dev/")

    def test_scrape_raises_connection_error(self):
        session = MagicMock()
        session.get.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(requests.exceptions.ConnectionError):
            scrape_page(session, "https://fashion-studio.dicoding.dev/")

    def test_scrape_retries_after_timeout_then_success(self):
        session = MagicMock()
        session.get.side_effect = [
            requests.exceptions.Timeout(),
            make_mock_response(SAMPLE_HTML),
        ]

        products = scrape_page(session, "https://fashion-studio.dicoding.dev/")

        assert len(products) == 2
        assert session.get.call_count == 2

    def test_scrape_retries_after_connection_error_then_success(self):
        session = MagicMock()
        session.get.side_effect = [
            requests.exceptions.ConnectionError(),
            make_mock_response(SAMPLE_HTML),
        ]

        products = scrape_page(session, "https://fashion-studio.dicoding.dev/")

        assert len(products) == 2
        assert session.get.call_count == 2

    def test_scrape_raises_http_error(self):
        session = MagicMock()
        mock_resp = make_mock_response("", status_code=404)
        mock_resp.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("404")
        )
        session.get.return_value = mock_resp

        with pytest.raises(requests.exceptions.HTTPError):
            scrape_page(session, "https://fashion-studio.dicoding.dev/")

    def test_scrape_empty_page(self):
        session = MagicMock()
        session.get.return_value = make_mock_response(
            "<html><body></body></html>"
        )

        products = scrape_page(session, "https://fashion-studio.dicoding.dev/")
        assert products == []

    @patch("utils.extract.parse_product_card")
    def test_scrape_page_skips_card_when_parse_fails(
        self,
        mock_parse_product_card
    ):
        session = MagicMock()
        session.get.return_value = make_mock_response(SAMPLE_HTML)

        mock_parse_product_card.side_effect = [
            Exception("parse error"),
            {
                "Title": "Recovered Product",
                "Price": "$100.00",
                "Rating": "⭐ 4.5 / 5",
                "Colors": "3 Colors",
                "Size": "Size: M",
                "Gender": "Gender: Men",
                "timestamp": "2024-01-01 00:00:00",
            },
        ]

        products = scrape_page(session, "https://fashion-studio.dicoding.dev/")

        assert len(products) == 1
        assert products[0]["Title"] == "Recovered Product"


# ── scrape_all_pages ─────────────────────────────────────────────────────────

class TestScrapeAllPages:
    @patch("utils.extract.requests.Session")
    def test_scrape_all_pages_calls_correct_number_of_pages(
        self,
        mock_session_cls
    ):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = make_mock_response(SAMPLE_HTML)

        result = scrape_all_pages(total_pages=3)

        assert mock_session.get.call_count == 3
        assert len(result) == 6

    @patch("utils.extract.requests.Session")
    def test_scrape_all_pages_skips_failed_page(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        ok_response = make_mock_response(SAMPLE_HTML)
        error_response = MagicMock()
        error_response.raise_for_status.side_effect = (
            requests.exceptions.HTTPError("500")
        )

        mock_session.get.side_effect = [
            ok_response,
            requests.exceptions.ConnectionError("fail"),
            ok_response,
        ]

        result = scrape_all_pages(total_pages=3)
        assert len(result) == 4

    @patch("utils.extract.requests.Session")
    def test_scrape_all_pages_returns_list(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        mock_session.get.return_value = make_mock_response(SAMPLE_HTML)

        result = scrape_all_pages(total_pages=1)
        assert isinstance(result, list)

    def test_scrape_all_pages_raises_for_zero_pages(self):
        with pytest.raises(ValueError):
            scrape_all_pages(total_pages=0)

    def test_scrape_all_pages_raises_for_negative_pages(self):
        with pytest.raises(ValueError):
            scrape_all_pages(total_pages=-1)

    def test_scrape_all_pages_raises_for_non_integer_pages(self):
        with pytest.raises(ValueError):
            scrape_all_pages(total_pages="3")
