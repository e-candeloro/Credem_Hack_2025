import logging

import pandas as pd
from config import load_config
from etl.pipeline import run_etl

# from exporter import zip_and_export
from gcs_utils import download_from_bucket, upload_to_bucket
from ocr.document_ai import all_process_documents_OVERPOWERED

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline orchestration function."""
    logger.info("Starting pipeline...")

    # 1. Load Configuration
    config = load_config()

    print(config)

    # 2. Download from GCS
    local_files = download_from_bucket(config)  # TODO ASYNC PARALLEL DOWNLOAD

    print("File loaded")
    # 3. OCR/Classification: Process documents
    extracted_data = all_process_documents_OVERPOWERED(config)

    extracted_data = pd.read_csv("data/extracted/extracted_data.csv")

    # 5. ETL: Process and transform data
    processed_string = run_etl(extracted_data, config)
    # processed_df.to_csv("final_data.csv", index=False)

    # # 6. Export: Zip results and upload to another GCS bucket
    # zip_path = zip_and_export(processed_string, config)

    # This is commented out for the same reason as the download step.
    # upload_to_bucket(zip_path, config['EXPORT_BUCKET'])

    logger.info(f"Pipeline finished successfully.")
    logger.info("In a real run, this zip would be uploaded to the export GCS bucket.")


if __name__ == "__main__":
    main()
