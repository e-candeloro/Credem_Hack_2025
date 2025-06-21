import os

from dotenv import load_dotenv


def load_config():
    """Loads configuration from environment variables."""
    load_dotenv()
    return {
        "PROJECT_ID": os.getenv("PROJECT_ID"),
        "LOCATION": os.getenv("LOCATION"),
        "INPUT_BUCKET": os.getenv("INPUT_BUCKET"),
        "OUTPUT_BUCKET": os.getenv("OUTPUT_BUCKET"),
        "PROCESSOR_ID": os.getenv("PROCESSOR_ID"),
    }
