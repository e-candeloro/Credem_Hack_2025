import pandas as pd


def load_file_as_bytes(file_path: str) -> bytes:
    """
    Loads the content of a local file as a bytes object.

    Args:
        file_path: The path to the local file.

    Returns:
        The content of the file as bytes.
    """
    try:
        with open(file_path, "rb") as f:
            content_bytes = f.read()
        return content_bytes
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return b""  # Return empty bytes or raise an exception
    except OSError as e:
        print(f"Error reading file '{file_path}': {e}")
        return b""  # Return empty bytes or raise an exception


def read_csv_from_gcs(name, bucket_name, data_prefix):
    return pd.read_csv(f"gs://{bucket_name}/{data_prefix}{name}")
