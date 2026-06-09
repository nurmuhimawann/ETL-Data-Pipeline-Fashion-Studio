import pytest

from config import (
    get_int_env,
    get_float_env,
    get_optional_env,
    get_required_env,
)


class TestConfig:
    def test_get_required_env_returns_value(self, monkeypatch):
        monkeypatch.setenv("SPREADSHEET_ID", "fake_id")

        result = get_required_env("SPREADSHEET_ID")

        assert result == "fake_id"

    def test_get_required_env_raises_when_missing(self, monkeypatch):
        monkeypatch.delenv("MISSING_KEY", raising=False)

        with pytest.raises(ValueError):
            get_required_env("MISSING_KEY")

    def test_get_int_env_returns_integer(self, monkeypatch):
        monkeypatch.setenv("TOTAL_PAGES", "50")

        result = get_int_env("TOTAL_PAGES", 10)

        assert result == 50

    def test_get_int_env_raises_for_non_integer(self, monkeypatch):
        monkeypatch.setenv("TOTAL_PAGES", "abc")

        with pytest.raises(ValueError):
            get_int_env("TOTAL_PAGES", 10)

    def test_get_int_env_raises_for_zero(self, monkeypatch):
        monkeypatch.setenv("TOTAL_PAGES", "0")

        with pytest.raises(ValueError):
            get_int_env("TOTAL_PAGES", 10)

    def test_get_float_env_returns_float(self, monkeypatch):
        monkeypatch.setenv("EXCHANGE_RATE", "16000")

        result = get_float_env("EXCHANGE_RATE", 15000)

        assert result == 16000.0

    def test_get_float_env_raises_for_non_number(self, monkeypatch):
        monkeypatch.setenv("EXCHANGE_RATE", "abc")

        with pytest.raises(ValueError):
            get_float_env("EXCHANGE_RATE", 15000)

    def test_get_float_env_raises_for_negative_number(self, monkeypatch):
        monkeypatch.setenv("EXCHANGE_RATE", "-16000")

        with pytest.raises(ValueError):
            get_float_env("EXCHANGE_RATE", 15000)

    def test_get_optional_env_returns_default_when_missing(self, monkeypatch):
        monkeypatch.delenv("OUTPUT_CSV", raising=False)

        result = get_optional_env("OUTPUT_CSV", "products.csv")

        assert result == "products.csv"

    def test_get_optional_env_returns_default_when_value_is_blank(
        self,
        monkeypatch
    ):
        monkeypatch.setenv("OUTPUT_CSV", "   ")

        result = get_optional_env("OUTPUT_CSV", "products.csv")

        assert result == "products.csv"

    def test_get_optional_env_returns_value_when_available(self, monkeypatch):
        monkeypatch.setenv("OUTPUT_CSV", "dicoding-fashion-products.csv")

        result = get_optional_env("OUTPUT_CSV", "products.csv")

        assert result == "dicoding-fashion-products.csv"
