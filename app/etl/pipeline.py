import logging

import pandas as pd
from utils.reading import read_csv_from_gcs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_etl(df_results, config):
    # Ensure columns exist before attempting to convert or merge
    if "Nome" in df_results.columns:
        df_results["Nome"] = df_results["Nome"].astype(str).str.lower()
    else:
        df_results["Nome"] = "Error"  # Handle missing column case

    if "Cognome" in df_results.columns:
        df_results["Cognome"] = df_results["Cognome"].astype(str).str.lower()
    else:
        df_results["Cognome"] = "Error"  # Handle missing column case

    df_cluster = read_csv_from_gcs("cluster.csv", config["INPUT_BUCKET"], "data/")
    df_personale = read_csv_from_gcs(
        "elenco_personale.csv", config["INPUT_BUCKET"], "data/"
    )

    if "Nome" in df_personale.columns:
        df_personale["Nome"] = df_personale["Nome"].astype(str).str.lower()
    else:
        print("Warning: 'Nome' column not found in 'elenco_personale.csv'.")

    if "Cognome" in df_personale.columns:
        df_personale["Cognome"] = df_personale["Cognome"].astype(str).str.lower()
    else:
        print("Warning: 'Cognome' column not found in 'elenco_personale.csv'.")

    df = pd.merge(df_results, df_cluster, on="Cluster", how="left")
    return pd.merge(
        df,
        df_personale,
        on=["Nome", "Cognome"],
        how="left",
        suffixes=("_doc", "_elenco"),
    )
