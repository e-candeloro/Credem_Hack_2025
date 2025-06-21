import logging
import os
from pathlib import Path
from typing import Union

import pandas as pd
from utils.reading import read_csv_from_gcs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_registry_df(
    df: pd.DataFrame,
    *,
    name_cols=("Nome", "Cognome"),  # columns to upper-case
    date_col="Data",
    country_col="Country",  # change if your column is called differently
) -> pd.DataFrame:
    """
    • Replace every spelling/spacing/casing of 'ERRORE' (and NaN/None) with placeholders
    • Convert valid dates → YYYY/MM/DD, invalid → 'ERRORE'
    • Upper-case names + country (placeholders already all-caps)
    Returns a *new* DataFrame.
    """

    # 1️⃣  normalise any variant of "ERRORE"
    df = df.applymap(
        lambda x: "ERRORE"
        if isinstance(x, str) and x.strip().upper() == "ERRORE"
        else x
    )

    # 2️⃣  placeholders for key columns
    placeholders = {
        "Nome": "NONAME",
        "Cognome": "NOLASTNAME",
        "Data": "NODATE",
        country_col: "",
    }
    for col, ph in placeholders.items():
        if col in df.columns:
            df[col] = df[col].fillna("ERRORE").replace("ERRORE", ph)

    # 3️⃣  robust date normalisation → YYYY/MM/DD
    if date_col in df.columns:

        def _format_date(v):
            if v in ("NODATE", "ERRORE"):
                return v
            try:
                dt = pd.to_datetime(v, errors="raise", dayfirst=False, utc=False)
                return dt.strftime("%Y/%m/%d")
            except Exception:
                return "ERRORE"

        df[date_col] = df[date_col].apply(_format_date)

    # 4️⃣  UPPER-case names
    for col in name_cols:
        if col in df.columns:
            ph = placeholders.get(col)
            df[col] = df[col].apply(lambda s: s if s == ph else str(s).strip().upper())

    # 5️⃣   Capitalize country with capitalize
    if country_col in df.columns:
        df[country_col] = df[country_col].apply(
            lambda s: s if s == ph else str(s).strip().capitalize()
        )

    return df


def combine_clean_data(df_results, df_personale):
    cols_section_1 = [
        "FILENAME",
        "METADATA",
        "DocumentsOfRecord",
        "PersonNumber",
        "DocumentType",
        "Country",
        "DocumentCode",
        "DocumentName",
        "DateFrom",
        "DateTo",
        "SourceSystemOwner",
        "SourceSystemId",
    ]
    df_section_1 = pd.DataFrame(columns=cols_section_1)

    cols_section_2 = [
        "FILENAME",
        "METADATA",
        "DocumentAttachment",
        "PersonNumber",
        "DocumentType",
        "Country",
        "DocumentCode",
        "DataTypeCode",
        "URLorTextorFileName",
        "Title",
        "File",
        "SourceSystemOwner",
        "SourceSystemId",
    ]
    df_section_2 = pd.DataFrame(columns=cols_section_2)

    for _, row_results in df_results.iterrows():
        # 1. Cerchiamo il match e dividiamo in due casi: match o non match
        # Per cercare il match, cerchiamo il match tra Nome e Cognome in df_personale. Se non c'è, allora è una riga speciale.
        # Riga speciale costruita con valori specifici e altri no.
        # 2. Se match, aggiungiamo i dati in df_section_1 i dati.
        match = False
        for _, row_personale in df_personale.iterrows():
            nome_pers = row_personale.get("Nome", "NONAME").strip().upper()
            cognome_pers = row_personale.get("Cognome", "NOLASTNAME").strip().upper()

            nome_res = row_results.get("Nome", "NONAME").strip().upper()
            cognome_res = row_results.get("Cognome", "NOLASTNAME").strip().upper()
            data_res = row_results.get("Data", "NODATE")

            if (
                nome_res == nome_pers
                and cognome_res == cognome_pers
                and data_res != "NODATE"
            ):
                # match
                match = True
                person_number = row_personale["Person Number"]
                document_type = row_results.get("Cluster", "Nessun cluster")
                country = row_results.get("Country", "")
                document_name = f"{cognome_res} {nome_res}".strip().upper()

        if not match:
            # non match
            person_number = "Nessun dipendente"
            document_type = "SCARTATO"
            country = ""
            document_name = "Nessun dipendente"
            document_code = "Nessun dipendente"

        # aggiungiamo i dati in comune per match e non match
        file_name = row_results["File_Name"]
        metadata = "MERGE"
        documents_of_records = "DocumentsOfRecords"
        date_from = row_results["Data"]
        date_normalized = date_from.replace("/", "").strip()
        document_code = f"{person_number}_{date_normalized}_{document_type}"
        date_to = ""
        source_system_owner = "PEOPLE"
        source_system_id = document_code
        document_attachment = "DocumentAttachment"

        # aggiungiamo i dati per la sezione 1
        # non usare append
        df_section_1.loc[len(df_section_1)] = [
            file_name,
            metadata,
            documents_of_records,
            person_number,
            document_type,
            country,
            document_code,
            document_name,
            date_from,
            date_to,
            source_system_owner,
            source_system_id,
        ]

        # salviamo la riga per il df_section_2

        data_type_code = "FILE"
        url_or_text_or_file_name = file_name
        title = file_name
        file = file_name

        df_section_2.loc[len(df_section_2)] = [
            file_name,
            metadata,
            document_attachment,
            person_number,
            document_type,
            country,
            document_code,
            data_type_code,
            url_or_text_or_file_name,
            title,
            file,
            source_system_owner,
            source_system_id,
        ]

    return df_section_1, df_section_2


def build_csv_string(df_sec_1: pd.DataFrame, df_sec_2: pd.DataFrame, sep="|") -> str:
    """
    Concatena i due dataframe in formato CSV (senza scrivere su disco)
    e restituisce una singola stringa.
    """
    csv1 = df_sec_1.to_csv(index=False, sep=sep)
    csv2 = df_sec_2.to_csv(index=False, sep=sep)
    return csv1 + csv2


def run_etl(df_results, config, eval=False):
    """
    Legacy function for backward compatibility.
    Now uses the new build_final_csv function.
    """
    # Save the extracted results to a temporary CSV
    os.makedirs("tmp/processed/", exist_ok=True)
    temp_extracted_path = "tmp/processed/ocr_extracted_results.csv"
    df_results.to_csv(temp_extracted_path, index=False)

    # Get the paths for the reference files
    personale_path = config["PERSONALE_PATH"]
    cluster_path = config["CLUSTERS_PATH"]
    # train_gt_path = config["TRAIN_GT_PATH"]

    df_personale = pd.read_csv(personale_path)

    # clean the df_results
    df_results = clean_registry_df(df_results)

    # combine the data
    df_sec_1, df_sec_2 = combine_clean_data(df_results, df_personale)

    # build the csv string
    csv_string = build_csv_string(df_sec_1, df_sec_2)

    # save the csv string
    with open(
        "tmp/processed/DocumentsOfRecord.dat",
        "w",
        newline="",
        encoding="utf-8",
    ) as f:
        f.write(csv_string)

    return csv_string
