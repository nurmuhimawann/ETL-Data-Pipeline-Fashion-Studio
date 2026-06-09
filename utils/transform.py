import logging
from typing import Any, Dict, List
import pandas as pd

EXCHANGE_RATE = 16000  # 1 USD = Rp16.000
REQUIRED_COLUMNS = [
    "Title",
    "Price",
    "Rating",
    "Colors",
    "Size",
    "Gender",
    "timestamp",
]
OUTPUT_COLUMNS = [
    "Title",
    "Price",
    "Rating",
    "Colors",
    "Size",
    "Gender",
    "timestamp",
]

logger = logging.getLogger(__name__)


def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def clean_title(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df[df["Title"].notna()].copy()
        df = df[df["Title"].str.strip() != ""].copy()
        df = df[df["Title"] != "Unknown Product"].copy()
        return df
    except Exception as e:
        raise ValueError(f"Error cleaning Title column: {e}")


def clean_price(
    df: pd.DataFrame,
    exchange_rate: float = EXCHANGE_RATE,
) -> pd.DataFrame:
    try:
        df = df[df["Price"].notna()].copy()
        df = df[df["Price"].str.strip() != "Price Unavailable"].copy()
        df = df[df["Price"].str.startswith("$", na=False)].copy()
        df["Price"] = df["Price"].str.replace("$", "", regex=False)
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df = df[df["Price"].notna()].copy()
        df["Price"] = df["Price"] * exchange_rate
        return df
    except Exception as e:
        raise ValueError(f"Error cleaning Price column: {e}")


def clean_rating(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df[df["Rating"].notna()].copy()
        rating_mask = df["Rating"].str.contains(
            "Invalid Rating|Not Rated",
            na=False,
        )
        df = df[~rating_mask].copy()
        df["Rating"] = pd.to_numeric(
            df["Rating"].str.extract(r"([\d.]+)")[0],
            errors="coerce",
        )
        df = df[df["Rating"].notna()].copy()
        return df
    except Exception as e:
        raise ValueError(f"Error cleaning Rating column: {e}")


def clean_colors(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df[df["Colors"].notna()].copy()
        df["Colors"] = pd.to_numeric(
            df["Colors"].str.extract(r"(\d+)")[0],
            errors="coerce",
        )
        df = df[df["Colors"].notna()].copy()
        df["Colors"] = df["Colors"].astype(int)
        return df
    except Exception as e:
        raise ValueError(f"Error cleaning Colors column: {e}")


def clean_size(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df[df["Size"].notna()].copy()
        df["Size"] = (
            df["Size"]
            .str.replace("Size:", "", regex=False)
            .str.strip()
        )
        df = df[df["Size"].str.strip() != ""]
        return df
    except Exception as e:
        raise ValueError(f"Error cleaning Size column: {e}")


def clean_gender(df: pd.DataFrame) -> pd.DataFrame:
    try:
        df = df[df["Gender"].notna()].copy()
        gender_series = df["Gender"].str.replace("Gender:", "", regex=False)
        df["Gender"] = gender_series.str.strip()
        df = df[df["Gender"].str.strip() != ""]
        return df
    except Exception as e:
        raise ValueError(f"Error cleaning Gender column: {e}")


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    try:
        before = len(df)
        duplicate_columns = [
            "Title",
            "Price",
            "Rating",
            "Colors",
            "Size",
            "Gender"
        ]
        df = df.drop_duplicates(subset=duplicate_columns).copy()
        after = len(df)
        logger.info("Removed %s duplicate rows.", before - after)
        return df
    except Exception as e:
        raise ValueError(f"Error removing duplicates: {e}")


def reset_index(df: pd.DataFrame) -> pd.DataFrame:
    try:
        return df.reset_index(drop=True)
    except Exception as e:
        raise ValueError(f"Error resetting index: {e}")


def transform(
    raw_data: List[Dict[str, Any]],
    exchange_rate: float = EXCHANGE_RATE,
) -> pd.DataFrame:
    try:
        df = pd.DataFrame(raw_data)
    except Exception as e:
        raise ValueError(f"Failed to create DataFrame from raw data: {e}")

    if df.empty:
        raise ValueError("No data to transform — DataFrame is empty.")

    validate_required_columns(df)

    df = clean_title(df)
    df = clean_price(df, exchange_rate=exchange_rate)
    df = clean_rating(df)
    df = clean_colors(df)
    df = clean_size(df)
    df = clean_gender(df)
    df = remove_duplicates(df)
    df = df.dropna()
    df = reset_index(df)

    df = df[OUTPUT_COLUMNS].copy()

    df["Title"] = df["Title"].astype("object")
    df["Price"] = df["Price"].astype(float)
    df["Rating"] = df["Rating"].astype(float)
    df["Colors"] = df["Colors"].astype(int)
    df["Size"] = df["Size"].astype("object")
    df["Gender"] = df["Gender"].astype("object")
    df["timestamp"] = df["timestamp"].astype(str)

    logger.info("Transformation complete. Remaining rows: %s", len(df))
    return df
