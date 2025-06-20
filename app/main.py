import logging

from config import load_config
from etl.pipeline import run_etl
from exporter import zip_and_export
from gcs_utils import download_from_bucket, upload_to_bucket
from ocr.document_ai import process_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main pipeline orchestration function."""
    logger.info("Starting pipeline...")

    # 1. Load Configuration
    config = load_config()

    # 2. Download from GCS
    local_files = download_from_bucket(config)

    print("File loaded")
    # 3. OCR/Classification: Process documents
    extracted_data = process_documents(config)

    # 5. ETL: Process and transform data
    processed_df = run_etl()

    # 6. Export: Zip results and upload to another GCS bucket
    zip_path = zip_and_export()

    # This is commented out for the same reason as the download step.
    # upload_to_bucket(zip_path, config['EXPORT_BUCKET'])

    logger.info(f"Pipeline finished successfully. Output zip is at {zip_path}")
    logger.info("In a real run, this zip would be uploaded to the export GCS bucket.")


if __name__ == "__main__":
    main()
