import os

from dotenv import load_dotenv


def load_config():
    """Loads configuration from environment variables."""
    load_dotenv()
    return {
        "DEBUG": os.getenv("DEBUG", "False"),
        "PROJECT_ID": os.getenv("PROJECT_ID", "credemhack-cloudfunctions"),
        "RUN_ID": os.getenv("RUN_ID"),
        "LOCATION": os.getenv("LOCATION", "us"),
        "INPUT_BUCKET": os.getenv("INPUT_BUCKET"),
        "OUTPUT_BUCKET": os.getenv("OUTPUT_BUCKET"),
        "PROCESSOR_ID": os.getenv("PROCESSOR_ID", "e4a86664fd2377e2"),
        "CLUSTERS_PATH": os.getenv("CLUSTERS_PATH", "etl_db_data/clusters.csv"),
        "TRAIN_GT_PATH": os.getenv("TRAIN_GT_PATH", "etl_db_data/doc_trains.csv"),
        "PERSONALE_PATH": os.getenv("PERSONALE_PATH", "etl_db_data/personale.csv"),
        "LLM_MODEL": os.getenv("LLM_MODEL", "gemini-2.5-pro"),
    }
