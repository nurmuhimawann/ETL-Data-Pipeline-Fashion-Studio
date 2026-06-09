import logging

from utils.extract import scrape_all_pages
from utils.transform import transform
from utils.load import save_to_csv, save_to_google_sheets
from config import (
    SPREADSHEET_ID,
    SERVICE_ACCOUNT_FILE,
    OUTPUT_CSV,
    TOTAL_PAGES,
    EXCHANGE_RATE,
    SHEET_NAME,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        logger.info("=" * 50)
        logger.info("ETL Pipeline — Fashion Studio")
        logger.info("=" * 50)

        logger.info("[EXTRACT] Mulai scraping data...")
        raw_data = scrape_all_pages(total_pages=TOTAL_PAGES)
        logger.info("[EXTRACT] Selesai. Total data mentah: %s", len(raw_data))

        logger.info("[TRANSFORM] Mulai transformasi data...")
        df = transform(raw_data, exchange_rate=EXCHANGE_RATE)
        logger.info("[TRANSFORM] Selesai. Total data bersih: %s", len(df))
        logger.info("Data types:\n%s", df.dtypes)

        logger.info("[LOAD] Menyimpan data...")
        save_to_csv(df, OUTPUT_CSV)
        save_to_google_sheets(
            df,
            SPREADSHEET_ID,
            SERVICE_ACCOUNT_FILE,
            sheet_name=SHEET_NAME,
        )

        logger.info("[DONE] ETL Pipeline selesai dijalankan.")

    except Exception as e:
        logger.exception("[ERROR] ETL Pipeline gagal dijalankan: %s", e)
        raise


if __name__ == "__main__":
    main()
