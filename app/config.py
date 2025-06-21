import os

from dotenv import load_dotenv


def load_config():
    """Loads configuration from environment variables."""
    load_dotenv()
    return {
        "DEBUG": os.getenv("DEBUG"),
        "PROJECT_ID": os.getenv("PROJECT_ID"),
        "LOCATION": os.getenv("LOCATION"),
        "INPUT_BUCKET": os.getenv("INPUT_BUCKET"),
        "OUTPUT_BUCKET": os.getenv("OUTPUT_BUCKET"),
        "PROCESSOR_ID": os.getenv("PROCESSOR_ID"),
        "LLM_MODEL": os.getenv("LLM_MODEL"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "CLUSTERS_PATH": os.getenv("CLUSTERS_PATH"),
        "TRAIN_GT_PATH": os.getenv("TRAIN_GT_PATH"),
        "PERSONALE_PATH": os.getenv("PERSONALE_PATH"),
    }
