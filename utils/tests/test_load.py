import os
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from utils.load import (
    save_to_csv,
    save_to_google_sheets,
    get_google_sheets_service,
    dataframe_to_sheet_values,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_df():
    return pd.DataFrame({
        "Title": ["T-shirt 1", "Pants 2"],
        "Price": [1600000.0, 3200000.0],
        "Rating": [4.5, 3.8],
        "Colors": [3, 5],
        "Size": ["M", "L"],
        "Gender": ["Men", "Women"],
        "timestamp": ["2024-01-01 00:00:00", "2024-01-01 00:00:00"],
    })


class TestDataFrameToSheetValues:
    def test_converts_dataframe_to_sheet_values(self):
        df = make_df()
        values = dataframe_to_sheet_values(df)

        assert values[0] == list(df.columns)
        assert len(values) == len(df) + 1
        assert values[1][0] == "T-shirt 1"

    def test_raises_on_empty_dataframe(self):
        with pytest.raises(ValueError):
            dataframe_to_sheet_values(pd.DataFrame())

    def test_raises_on_none_dataframe(self):
        with pytest.raises(ValueError):
            dataframe_to_sheet_values(None)

    def test_raises_runtime_error_when_dataframe_conversion_fails(self):
        df = make_df()

        with patch.object(
            pd.DataFrame,
            "astype",
            side_effect=Exception("conversion error"),
        ):
            with pytest.raises(RuntimeError, match="Failed to convert"):
                dataframe_to_sheet_values(df)


# ── save_to_csv ──────────────────────────────────────────────────────────────

class TestSaveToCsv:
    def test_saves_csv_file(self, tmp_path):
        df = make_df()
        filepath = str(tmp_path / "test_output.csv")
        save_to_csv(df, filepath)
        assert os.path.exists(filepath)

    def test_csv_contains_correct_rows(self, tmp_path):
        df = make_df()
        filepath = str(tmp_path / "test_output.csv")
        save_to_csv(df, filepath)
        loaded = pd.read_csv(filepath)
        assert len(loaded) == 2
        assert list(loaded.columns) == list(df.columns)

    def test_save_csv_raises_on_empty_df(self, tmp_path):
        df = pd.DataFrame()
        filepath = str(tmp_path / "empty.csv")
        with pytest.raises(RuntimeError):
            save_to_csv(df, filepath)

    def test_save_csv_raises_on_none(self, tmp_path):
        filepath = str(tmp_path / "none.csv")
        with pytest.raises(RuntimeError):
            save_to_csv(None, filepath)


# ── get_google_sheets_service ───────────────────────────────────────────────

class TestGetGoogleSheetsService:
    @patch("utils.load.os.path.exists", return_value=False)
    def test_raises_if_service_account_not_found(self, mock_exists):
        with pytest.raises(FileNotFoundError):
            get_google_sheets_service("nonexistent.json")

    @patch("utils.load.build")
    @patch("utils.load.Credentials.from_service_account_file")
    @patch("utils.load.os.path.exists", return_value=True)
    def test_returns_service_when_file_exists(
        self, mock_exists, mock_creds, mock_build
    ):
        mock_creds.return_value = MagicMock()
        mock_build.return_value = MagicMock()

        service = get_google_sheets_service("google-sheets-api.json")
        assert service is not None
        mock_build.assert_called_once()

    @patch(
        "utils.load.Credentials.from_service_account_file",
        side_effect=Exception("credential error"),
    )
    @patch("utils.load.os.path.exists", return_value=True)
    def test_raises_runtime_error_when_credentials_fail(
        self,
        mock_exists,
        mock_credentials,
    ):
        with pytest.raises(RuntimeError, match="Failed to initialize"):
            get_google_sheets_service("google-sheets-api.json")


# ── save_to_google_sheets ────────────────────────────────────────────────────

class TestSaveToGoogleSheets:
    def _mock_service(self):
        """Build a mock Google Sheets service."""
        mock_service = MagicMock()
        mock_sheets = mock_service.spreadsheets.return_value
        mock_values = mock_sheets.values.return_value
        mock_values.clear.return_value.execute.return_value = {}
        mock_values.update.return_value.execute.return_value = {}
        return mock_service

    @patch("utils.load.get_google_sheets_service")
    def test_calls_clear_and_update(self, mock_get_service):
        mock_service = self._mock_service()
        mock_get_service.return_value = mock_service
        df = make_df()

        save_to_google_sheets(df, "fake_spreadsheet_id")

        mock_get_service.assert_called_once()

        mock_values = (
            mock_service.spreadsheets.return_value.values.return_value
        )

        mock_values.clear.assert_called_once_with(
            spreadsheetId="fake_spreadsheet_id",
            range="Sheet1",
        )

        mock_values.update.assert_called_once()

        update_kwargs = mock_values.update.call_args.kwargs

        assert update_kwargs["spreadsheetId"] == "fake_spreadsheet_id"
        assert update_kwargs["range"] == "Sheet1!A1"
        assert update_kwargs["valueInputOption"] == "RAW"
        assert "body" in update_kwargs
        assert "values" in update_kwargs["body"]

    @patch("utils.load.get_google_sheets_service")
    def test_raises_on_empty_df(self, mock_get_service):
        with pytest.raises(ValueError):
            save_to_google_sheets(pd.DataFrame(), "fake_spreadsheet_id")

    @patch("utils.load.get_google_sheets_service")
    def test_raises_on_none_df(self, mock_get_service):
        with pytest.raises(ValueError):
            save_to_google_sheets(None, "fake_spreadsheet_id")

    @patch("utils.load.get_google_sheets_service")
    def test_raises_on_empty_spreadsheet_id(self, mock_get_service):
        with pytest.raises(ValueError):
            save_to_google_sheets(make_df(), "")

    @patch("utils.load.get_google_sheets_service")
    def test_raises_on_none_spreadsheet_id(self, mock_get_service):
        with pytest.raises(ValueError):
            save_to_google_sheets(make_df(), None)

    @patch("utils.load.get_google_sheets_service")
    def test_raises_on_empty_sheet_name(self, mock_get_service):
        with pytest.raises(ValueError):
            save_to_google_sheets(
                make_df(), "fake_spreadsheet_id", sheet_name=""
            )

    @patch("utils.load.get_google_sheets_service")
    def test_uses_custom_sheet_name(self, mock_get_service):
        mock_service = self._mock_service()
        mock_get_service.return_value = mock_service
        df = make_df()

        save_to_google_sheets(df, "fake_spreadsheet_id", sheet_name="Products")

        mock_values = (
            mock_service.spreadsheets.return_value.values.return_value
        )

        mock_values.clear.assert_called_once_with(
            spreadsheetId="fake_spreadsheet_id",
            range="Products",
        )

        update_kwargs = mock_values.update.call_args.kwargs
        assert update_kwargs["range"] == "Products!A1"

    @patch("utils.load.get_google_sheets_service")
    def test_raises_runtime_error_on_api_failure(self, mock_get_service):
        mock_service = MagicMock()
        clear_call = (
            mock_service.spreadsheets.return_value.values.return_value
            .clear.return_value.execute
        )
        clear_call.side_effect = Exception("API error")
        mock_get_service.return_value = mock_service

        with pytest.raises(RuntimeError):
            save_to_google_sheets(make_df(), "fake_id")

    def test_raises_file_not_found_when_no_service_account(self):
        with patch("utils.load.os.path.exists", return_value=False):
            with pytest.raises((FileNotFoundError, RuntimeError)):
                save_to_google_sheets(make_df(), "fake_id", "nonexistent.json")
