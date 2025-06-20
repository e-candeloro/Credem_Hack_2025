import logging
import os

from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_from_bucket(config: dict) -> list[str]:
    """Downloads files from a GCS bucket to a local directory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(config["INPUT_BUCKET"])

    # Create a local temp directory if it doesn't exist
    local_tmp_dir = "/tmp/pipeline_input"
    os.makedirs(local_tmp_dir, exist_ok=True)

    logger.info(
        f"Downloading files from gs://{config['INPUT_BUCKET']} to {local_tmp_dir}..."
    )

    downloaded_files = []
    for blob in bucket.list_blobs():
        file_path = os.path.join(local_tmp_dir, os.path.basename(blob.name))
        blob.download_to_filename(file_path)
        downloaded_files.append(file_path)
        logger.info(f"Downloaded {blob.name}")

    return downloaded_files


def upload_to_bucket(file_path: str, bucket_name: str):
    """Uploads a file to a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(file_path))

    logger.info(f"Uploading {file_path} to gs://{bucket_name}...")
    blob.upload_from_filename(file_path)
    logger.info("Upload complete.")
