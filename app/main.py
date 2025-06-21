import logging

import pandas as pd
from config import load_config
from etl.pipeline import run_etl
from exporter import zip_and_upload
from gcs_utils import download_from_bucket, upload_to_bucket
from ocr.document_ai import all_process_documents_OVERPOWERED

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline orchestration function."""
    logger.info("Starting pipeline...")

    # 1. Load Configuration
    config = load_config()
    logger.info(f"Configuration loaded: {config}")

    # 2. Download from GCS
    logger.info("Starting GCS download...")
    local_files = download_from_bucket(config)  # TODO ASYNC PARALLEL DOWNLOAD
    logger.info(f"Downloaded {len(local_files)} files: {local_files}")

    print("File loaded")
    # 3. OCR/Classification: Process documents
    logger.info("Starting OCR/Classification processing...")
    extracted_data = all_process_documents_OVERPOWERED(config)
    logger.info(f"OCR processing completed.")

    # extracted_data = pd.read_csv("data/extracted/extracted_data.csv")

    # 5. ETL: Process and transform data
    logger.info("Starting ETL processing...")
    processed_string = run_etl(extracted_data, config)
    # processed_df.to_csv("final_data.csv", index=False)

    # # 6. Export: Zip results and upload to another GCS bucket
    logger.info("Starting export process...")
    zip_path = zip_and_upload(metadata=processed_string, config=config)

    logger.info(f"Pipeline finished successfully.")
    logger.info(
        f"In a real run, this zip would be uploaded to the export GCS bucket in the folder: {zip_path}"
    )


if __name__ == "__main__":
    main()
