import pytest
import pandas as pd
from utils.transform import (
    clean_title,
    clean_price,
    clean_rating,
    clean_colors,
    clean_size,
    clean_gender,
    remove_duplicates,
    reset_index,
    validate_required_columns,
    transform,
    EXCHANGE_RATE,
    OUTPUT_COLUMNS,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_raw_data(n=3):
    """Return list of valid raw product dicts."""
    return [
        {
            "Title": f"T-shirt {i}",
            "Price": f"${100.0 + i:.2f}",
            "Rating": f"⭐ {3.5 + i * 0.1:.1f} / 5",
            "Colors": f"{i + 1} Colors",
            "Size": "Size: M",
            "Gender": "Gender: Men",
            "timestamp": "2024-01-01 00:00:00",
        }
        for i in range(1, n + 1)
    ]


def make_df(overrides=None):
    data = make_raw_data()
    df = pd.DataFrame(data)
    if overrides:
        for col, val in overrides.items():
            df[col] = val
    return df


class TestValidateRequiredColumns:
    def test_passes_when_all_required_columns_exist(self):
        df = pd.DataFrame(make_raw_data(3))

        validate_required_columns(df)

    def test_raises_when_required_column_is_missing(self):
        df = pd.DataFrame(make_raw_data(3))
        df = df.drop(columns=["Price"])

        with pytest.raises(ValueError, match="Missing required columns"):
            validate_required_columns(df)


# ── clean_title ──────────────────────────────────────────────────────────────

class TestCleanTitle:
    def test_removes_unknown_product(self):
        df = make_df({"Title": ["Unknown Product", "T-shirt 1", "Pants 1"]})
        result = clean_title(df)
        assert "Unknown Product" not in result["Title"].values
        assert len(result) == 2

    def test_removes_null_title(self):
        df = make_df({"Title": [None, "T-shirt 1", "Pants 1"]})
        result = clean_title(df)
        assert len(result) == 2

    def test_removes_empty_title(self):
        df = make_df({"Title": ["", "T-shirt 1", "Pants 1"]})
        result = clean_title(df)
        assert len(result) == 2

    def test_keeps_valid_titles(self):
        df = pd.DataFrame(make_raw_data())
        result = clean_title(df)
        assert len(result) == 3


# ── clean_price ──────────────────────────────────────────────────────────────

class TestCleanPrice:
    def test_converts_usd_to_idr(self):
        df = make_df({"Price": ["$100.00", "$200.00", "$50.00"]})
        result = clean_price(df)
        assert result["Price"].iloc[0] == 100.00 * EXCHANGE_RATE
        assert result["Price"].iloc[1] == 200.00 * EXCHANGE_RATE

    def test_converts_price_using_custom_exchange_rate(self):
        df = make_df({"Price": ["$100.00", "$200.00", "$50.00"]})
        result = clean_price(df, exchange_rate=15000)

        assert result["Price"].iloc[0] == 100.00 * 15000
        assert result["Price"].iloc[1] == 200.00 * 15000

    def test_removes_price_unavailable(self):
        df = make_df({"Price": ["Price Unavailable", "$100.00", "$200.00"]})
        result = clean_price(df)
        assert len(result) == 2

    def test_removes_null_price(self):
        df = make_df({"Price": [None, "$100.00", "$200.00"]})
        result = clean_price(df)
        assert len(result) == 2

    def test_price_column_is_float(self):
        df = make_df({"Price": ["$100.00", "$200.00", "$300.00"]})
        result = clean_price(df)
        assert result["Price"].dtype == float


# ── clean_rating ─────────────────────────────────────────────────────────────

class TestCleanRating:
    def test_extracts_float_from_rating(self):
        df = make_df({"Rating": ["⭐ 4.5 / 5", "⭐ 3.8 / 5", "⭐ 5.0 / 5"]})
        result = clean_rating(df)
        assert result["Rating"].iloc[0] == 4.5
        assert result["Rating"].iloc[1] == 3.8

    def test_removes_invalid_rating(self):
        ratings = [
            "⭐ Invalid Rating / 5",
            "⭐ 4.5 / 5",
            "⭐ 3.8 / 5",
        ]
        df = make_df({"Rating": ratings})
        result = clean_rating(df)
        assert len(result) == 2

    def test_removes_not_rated(self):
        df = make_df({"Rating": ["Not Rated", "⭐ 4.5 / 5", "⭐ 3.8 / 5"]})
        result = clean_rating(df)
        assert len(result) == 2

    def test_removes_null_rating(self):
        df = make_df({"Rating": [None, "⭐ 4.5 / 5", "⭐ 3.8 / 5"]})
        result = clean_rating(df)
        assert len(result) == 2

    def test_rating_column_is_float(self):
        df = make_df({"Rating": ["⭐ 4.5 / 5", "⭐ 3.8 / 5", "⭐ 5.0 / 5"]})
        result = clean_rating(df)
        assert result["Rating"].dtype == float


# ── clean_colors ─────────────────────────────────────────────────────────────

class TestCleanColors:
    def test_extracts_number_from_colors(self):
        df = make_df({"Colors": ["3 Colors", "5 Colors", "8 Colors"]})
        result = clean_colors(df)
        assert result["Colors"].iloc[0] == 3
        assert result["Colors"].iloc[1] == 5

    def test_removes_null_colors(self):
        df = make_df({"Colors": [None, "3 Colors", "5 Colors"]})
        result = clean_colors(df)
        assert len(result) == 2

    def test_colors_column_is_int(self):
        df = make_df({"Colors": ["3 Colors", "5 Colors", "8 Colors"]})
        result = clean_colors(df)
        assert result["Colors"].dtype == int


# ── clean_size ───────────────────────────────────────────────────────────────

class TestCleanSize:
    def test_removes_size_prefix(self):
        df = make_df({"Size": ["Size: M", "Size: L", "Size: XL"]})
        result = clean_size(df)
        assert result["Size"].iloc[0] == "M"
        assert result["Size"].iloc[1] == "L"

    def test_removes_null_size(self):
        df = make_df({"Size": [None, "Size: M", "Size: L"]})
        result = clean_size(df)
        assert len(result) == 2

    def test_removes_empty_size(self):
        df = make_df({"Size": ["", "Size: M", "Size: L"]})
        result = clean_size(df)
        assert len(result) == 2


# ── clean_gender ──────────────────────────────────────────────────────────

class TestCleanGender:
    def test_removes_gender_prefix(self):
        df = make_df({
            "Gender": [
                "Gender: Men",
                "Gender: Women",
                "Gender: Unisex",
            ]
        })
        result = clean_gender(df)
        assert result["Gender"].iloc[0] == "Men"
        assert result["Gender"].iloc[1] == "Women"

    def test_removes_null_gender(self):
        df = make_df({"Gender": [None, "Gender: Men", "Gender: Women"]})
        result = clean_gender(df)
        assert len(result) == 2

    def test_removes_empty_gender(self):
        df = make_df({"Gender": ["", "Gender: Men", "Gender: Women"]})
        result = clean_gender(df)
        assert len(result) == 2


# ── remove_duplicates ──────────────────────────────────────────────────────

class TestRemoveDuplicates:
    def test_removes_duplicate_rows(self):
        raw = make_raw_data(2)
        raw.append(raw[0].copy())
        df = pd.DataFrame(raw)
        result = remove_duplicates(df)
        assert len(result) == 2

    def test_no_duplicates_unchanged(self):
        df = pd.DataFrame(make_raw_data(3))
        result = remove_duplicates(df)
        assert len(result) == 3

    def test_remove_duplicates_ignores_timestamp(self):
        df = pd.DataFrame([
            {
                "Title": "T-shirt 1",
                "Price": 1800000.0,
                "Rating": 4.5,
                "Colors": 3,
                "Size": "M",
                "Gender": "Men",
                "timestamp": "2024-01-01 00:00:00",
            },
            {
                "Title": "T-shirt 1",
                "Price": 1800000.0,
                "Rating": 4.5,
                "Colors": 3,
                "Size": "M",
                "Gender": "Men",
                "timestamp": "2024-01-02 00:00:00",
            },
        ])
        result = remove_duplicates(df)
        assert len(result) == 1


# ── reset_index ──────────────────────────────────────────────────────────────

class TestResetIndex:
    def test_index_starts_at_zero(self):
        df = pd.DataFrame(make_raw_data(3)).iloc[1:]
        result = reset_index(df)
        assert list(result.index) == [0, 1]


# ── transform (full pipeline) ────────────────────────────────────────────────

class TestTransform:
    def test_transform_returns_dataframe(self):
        raw = make_raw_data(5)
        result = transform(raw)
        assert isinstance(result, pd.DataFrame)

    def test_transform_correct_dtypes(self):
        raw = make_raw_data(3)
        result = transform(raw)
        assert result["Price"].dtype == float
        assert result["Rating"].dtype == float
        assert result["Colors"].dtype == int
        assert result["Title"].dtype == object
        assert result["Size"].dtype == object
        assert result["Gender"].dtype == object

    def test_transform_removes_invalid_data(self):
        raw = make_raw_data(3)
        raw.append({
            "Title": "Unknown Product",
            "Price": "Price Unavailable",
            "Rating": "⭐ Invalid Rating / 5",
            "Colors": "3 Colors",
            "Size": "Size: M",
            "Gender": "Gender: Men",
            "timestamp": "2024-01-01 00:00:00",
        })
        result = transform(raw)
        assert "Unknown Product" not in result["Title"].values

    def test_transform_price_in_idr(self):
        raw = make_raw_data(1)
        result = transform(raw)
        assert result["Price"].iloc[0] == 101.0 * EXCHANGE_RATE

    def test_transform_uses_custom_exchange_rate(self):
        raw = make_raw_data(1)
        result = transform(raw, exchange_rate=15000)

        assert result["Price"].iloc[0] == 101.0 * 15000

    def test_transform_has_timestamp_column(self):
        raw = make_raw_data(3)
        result = transform(raw)
        assert "timestamp" in result.columns

    def test_transform_returns_expected_column_order(self):
        raw = make_raw_data(3)
        result = transform(raw)

        assert list(result.columns) == OUTPUT_COLUMNS

    def test_transform_raises_on_empty_data(self):
        with pytest.raises(ValueError):
            transform([])

    def test_transform_no_nulls(self):
        raw = make_raw_data(5)
        result = transform(raw)
        assert result.isnull().sum().sum() == 0

    def test_transform_no_duplicates(self):
        raw = make_raw_data(3)
        raw_with_dup = raw + [raw[0].copy()]
        result = transform(raw_with_dup)
        assert len(result) == len(result.drop_duplicates())


class TestTransformErrorHandling:
    def test_clean_title_raises_value_error_when_title_column_missing(self):
        df = make_df().drop(columns=["Title"])

        with pytest.raises(ValueError, match="Error cleaning Title column"):
            clean_title(df)

    def test_clean_price_raises_value_error_when_price_column_missing(self):
        df = make_df().drop(columns=["Price"])

        with pytest.raises(ValueError, match="Error cleaning Price column"):
            clean_price(df)

    def test_clean_rating_raises_value_error_when_rating_column_missing(self):
        df = make_df().drop(columns=["Rating"])

        with pytest.raises(ValueError, match="Error cleaning Rating column"):
            clean_rating(df)

    def test_clean_colors_raises_value_error_when_colors_column_missing(self):
        df = make_df().drop(columns=["Colors"])

        with pytest.raises(ValueError, match="Error cleaning Colors column"):
            clean_colors(df)

    def test_clean_size_raises_value_error_when_size_column_missing(self):
        df = make_df().drop(columns=["Size"])

        with pytest.raises(ValueError, match="Error cleaning Size column"):
            clean_size(df)

    def test_clean_gender_raises_value_error_when_gender_column_missing(self):
        df = make_df().drop(columns=["Gender"])

        with pytest.raises(ValueError, match="Error cleaning Gender column"):
            clean_gender(df)

    def test_remove_duplicates_raises_value_error_when_subset_column_missing(
        self,
    ):
        df = make_df().drop(columns=["Gender"])

        with pytest.raises(ValueError, match="Error removing duplicates"):
            remove_duplicates(df)

    def test_reset_index_raises_value_error_when_reset_fails(self):
        class BadDataFrame:
            def reset_index(self, drop=True):
                raise Exception("reset failed")

        with pytest.raises(ValueError, match="Error resetting index"):
            reset_index(BadDataFrame())

    def test_transform_raises_when_dataframe_creation_fails(self):
        with pytest.raises(ValueError, match="Failed to create DataFrame"):
            transform(object())
