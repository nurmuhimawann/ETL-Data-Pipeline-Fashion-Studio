import pytest
import pandas as pd
from unittest.mock import patch

import main


@patch("main.save_to_google_sheets")
@patch("main.save_to_csv")
@patch("main.transform")
@patch("main.scrape_all_pages")
def test_main_runs_pipeline_successfully(
    mock_scrape_all_pages,
    mock_transform,
    mock_save_to_csv,
    mock_save_to_google_sheets,
):
    raw_data = [
        {
            "Title": "T-shirt 1",
            "Price": "$100.00",
            "Rating": "⭐ 4.5 / 5",
            "Colors": "3 Colors",
            "Size": "Size: M",
            "Gender": "Gender: Men",
            "timestamp": "2024-01-01 00:00:00",
        }
    ]

    df = pd.DataFrame({
        "Title": ["T-shirt 1"],
        "Price": [1800000.0],
        "Rating": [4.5],
        "Colors": [3],
        "Size": ["M"],
        "Gender": ["Men"],
        "timestamp": ["2024-01-01 00:00:00"],
    })

    mock_scrape_all_pages.return_value = raw_data
    mock_transform.return_value = df

    main.main()

    mock_scrape_all_pages.assert_called_once_with(
        total_pages=main.TOTAL_PAGES
    )
    mock_transform.assert_called_once_with(
        raw_data,
        exchange_rate=main.EXCHANGE_RATE,
    )
    mock_save_to_csv.assert_called_once_with(
        df,
        main.OUTPUT_CSV,
    )
    mock_save_to_google_sheets.assert_called_once_with(
        df,
        main.SPREADSHEET_ID,
        main.SERVICE_ACCOUNT_FILE,
        sheet_name=main.SHEET_NAME,
    )


@patch("main.scrape_all_pages", side_effect=Exception("scrape failed"))
def test_main_raises_when_pipeline_fails(mock_scrape_all_pages):
    with pytest.raises(Exception, match="scrape failed"):
        main.main()
