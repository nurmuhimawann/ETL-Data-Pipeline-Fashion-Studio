import os
import logging
from typing import Any, List

import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_CSV_PATH = "products.csv"
SERVICE_ACCOUNT_FILE = "google-sheets-api.json"
DEFAULT_SHEET_NAME = "Sheet1"

logger = logging.getLogger(__name__)


def save_to_csv(df: pd.DataFrame, filepath: str = DEFAULT_CSV_PATH) -> None:
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame is empty — nothing to save to CSV.")
        df.to_csv(filepath, index=False)
        logger.info("Data saved to CSV: %s (%s rows)", filepath, len(df))
    except Exception as e:
        raise RuntimeError(f"Failed to save data to CSV: {e}")


def get_google_sheets_service(
    service_account_file: str = SERVICE_ACCOUNT_FILE,
) -> Any:
    try:
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(
                f"Service account file not found: {service_account_file}"
            )
        creds = Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES
        )
        service = build("sheets", "v4", credentials=creds)
        return service
    except FileNotFoundError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Google Sheets service: {e}")


def dataframe_to_sheet_values(df: pd.DataFrame) -> List[List[str]]:
    try:
        if df is None or df.empty:
            raise ValueError("DataFrame is empty — nothing to convert.")

        headers = df.columns.tolist()
        rows = df.astype(str).values.tolist()

        return [headers] + rows
    except ValueError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to convert DataFrame to sheet values: {e}")


def save_to_google_sheets(
    df: pd.DataFrame,
    spreadsheet_id: str,
    service_account_file: str = SERVICE_ACCOUNT_FILE,
    sheet_name: str = DEFAULT_SHEET_NAME,
) -> None:
    try:
        if df is None or df.empty:
            raise ValueError(
                "DataFrame is empty — nothing to save to Google Sheets."
            )

        if not spreadsheet_id or not str(spreadsheet_id).strip():
            raise ValueError("Spreadsheet ID is required.")

        if not sheet_name or not str(sheet_name).strip():
            raise ValueError("Sheet name is required.")

        service = get_google_sheets_service(service_account_file)
        values = dataframe_to_sheet_values(df)

        body = {"values": values}

        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
        ).execute()

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body=body,
        ).execute()

        logger.info(
            "Data saved to Google Sheets (ID: %s, Sheet: %s) — %s rows",
            spreadsheet_id,
            sheet_name,
            len(df),
        )
    except (ValueError, FileNotFoundError):
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to save data to Google Sheets: {e}")
