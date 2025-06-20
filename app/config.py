import os

from dotenv import load_dotenv


def load_config():
    """Loads configuration from environment variables."""
    load_dotenv()
    return {
        "PROJECT_ID": os.getenv("PROJECT_ID"),
        "GCP_REGION": os.getenv("GCP_REGION"),
        "INPUT_BUCKET": os.getenv("INPUT_BUCKET"),
        "OUTPUT_BUCKET": os.getenv("OUTPUT_BUCKET"),
        "DOCAI_PROCESSOR_ID": os.getenv("DOCAI_PROCESSOR_ID"),
    }
