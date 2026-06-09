import os
from dotenv import load_dotenv


load_dotenv()


def get_required_env(key: str) -> str:
    value = os.getenv(key)

    if value is None or not value.strip():
        raise ValueError(f"{key} is required.")

    return value


def get_int_env(key: str, default: int) -> int:
    value = os.getenv(key, str(default))

    try:
        parsed_value = int(value)
    except ValueError:
        raise ValueError(f"{key} must be an integer.")

    if parsed_value < 1:
        raise ValueError(f"{key} must be a positive integer.")

    return parsed_value


def get_float_env(key: str, default: float) -> float:
    value = os.getenv(key, str(default))

    try:
        parsed_value = float(value)
    except ValueError:
        raise ValueError(f"{key} must be a number.")

    if parsed_value <= 0:
        raise ValueError(f"{key} must be greater than zero.")

    return parsed_value


def get_optional_env(key: str, default: str) -> str:
    value = os.getenv(key, default)

    if not value or not value.strip():
        return default

    return value


SPREADSHEET_ID = get_required_env("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = get_optional_env(
    "SERVICE_ACCOUNT_FILE",
    "google-sheets-api.json",
)
OUTPUT_CSV = get_optional_env(
    "OUTPUT_CSV",
    "dicoding-fashion-products.csv",
)
TOTAL_PAGES = get_int_env("TOTAL_PAGES", 50)
EXCHANGE_RATE = get_float_env("EXCHANGE_RATE", 16000)
SHEET_NAME = get_optional_env("SHEET_NAME", "Sheet1")
