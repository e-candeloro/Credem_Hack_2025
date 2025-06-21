import logging
import os

from google.cloud import storage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GCS_INPUT_PREFIX = "input/"
GCS_DATA_PREFIX = "data/"


def download_from_bucket(config: dict) -> list[str]:
    """Downloads files from a GCS bucket to a local directory."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(config["INPUT_BUCKET"])

    local_tmp_dir = "tmp/"
    os.makedirs(local_tmp_dir, exist_ok=True)

    logger.info(
        f"Downloading files from gs://{config['INPUT_BUCKET']} to {local_tmp_dir}..."
    )
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Absolute path to tmp directory: {os.path.abspath(local_tmp_dir)}")

    downloaded_files = []
    exts = (".pdf", ".tif", ".tiff", ".png", ".jpeg", ".jpg")
    blobs = [b for b in bucket.list_blobs() if b.name.lower().endswith(exts)]

    logger.info(f"Found {len(blobs)} files in bucket with extensions {exts}")

    for blob in blobs:
        # --- IMPORTANT: Skip blobs that are GCS directory markers ---
        if blob.name.endswith("/"):
            logger.info(f"Skipping directory marker: {blob.name}")
            continue

        file_path = os.path.join(local_tmp_dir, os.path.basename(blob.name))
        try:
            blob.download_to_filename(file_path)
            downloaded_files.append(file_path)
            logger.info(f"Downloaded {blob.name} to {file_path}")
        except Exception as e:
            logger.error(f"Error downloading {blob.name} to {file_path}: {e}")
            # Depending on your needs, you might want to:
            # - continue (skip to next blob)
            # - raise (stop execution)
            # - log and ignore
            raise  # Re-raising for now to ensure errors are caught during development

    logger.info(f"Successfully downloaded {len(downloaded_files)} files")
    return downloaded_files


def upload_to_bucket(file_path: str, bucket_name: str):
    """Uploads a file to a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(os.path.basename(file_path))

    logger.info(f"Uploading {file_path} to gs://{bucket_name}...")
    blob.upload_from_filename(file_path)
    logger.info("Upload complete.")
