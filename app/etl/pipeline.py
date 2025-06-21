import logging
from pathlib import Path
from typing import Union

import pandas as pd
from utils.reading import read_csv_from_gcs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLACEHOLDERS = {
    "Nome": "NONAME",
    "Cognome": "NOLASTNAME",
    "Data": "NODATE",
}


def _is_ph(value: str, bad={"NONAME", "NOLASTNAME", "NODATE", "ERRORE"}) -> bool:
    return str(value).strip().upper() in bad


def build_final_csv(
    extracted_csv: str | Path,
    personale_csv: str | Path,
    *,
    out_path: str | Path = "final_documents.csv",
    cluster_col: str = "Cluster",  # dove trovo il DocumentType
    country_col: str = "Country Document HCM",  # dove trovo il Country
) -> pd.DataFrame:
    """
    • Carica i due file (estratti + anagrafica personale)
    • Ripulisce placeholder, date, maiuscole
    • Esegue il join su NOME & COGNOME mantenendo i valori già processati
    • Applica le regole speciali (dipendente non trovato, placeholder, ecc.)
    • Scrive e restituisce il CSV con 12 colonne:
      FILENAME | METADATA | DocumentsOfRecord | PersonNumber | DocumentType |
      Country | DocumentCode | DocumentName | DateFrom | DateTo |
      SourceSystemOwner | SourceSystemId
    """
    # ---------- LOAD & NORMALISE ----------
    df_ext = pd.read_csv(extracted_csv, dtype=str).fillna("ERRORE")
    df_pers = pd.read_csv(personale_csv, dtype=str).fillna("")

    # uniforma placeholder / capitalizzazione
    for col, ph in PLACEHOLDERS.items():
        if col in df_ext.columns:
            df_ext[col] = (
                df_ext[col]
                .apply(lambda x: ph if str(x).strip().upper() == "ERRORE" else x)
                .str.strip()
                .str.upper()
            )
    for col in ("Nome", "Cognome"):
        if col in df_pers.columns:
            df_pers[col] = df_pers[col].str.strip().str.upper()

    # Date in YYYY/MM/DD o placeholder
    if "Data" in df_ext.columns:

        def _fmt_date(x):
            if _is_ph(x):
                return "NODATE"
            try:
                return pd.to_datetime(x, errors="raise").strftime("%Y/%m/%d")
            except Exception:
                return "ERRORE"

        df_ext["Data"] = df_ext["Data"].apply(_fmt_date)

    # ---------- JOIN ----------
    df_ok = df_ext[
        ~df_ext.apply(
            lambda r: _is_ph(r["Nome"]) or _is_ph(r["Cognome"]) or _is_ph(r["Data"]),
            axis=1,
        )
    ]
    df_bad = df_ext[
        df_ext.apply(
            lambda r: _is_ph(r["Nome"]) or _is_ph(r["Cognome"]) or _is_ph(r["Data"]),
            axis=1,
        )
    ]  # con placeholder → "dip. non trovato"

    df_join = df_ok.merge(df_pers, on=["Nome", "Cognome"], how="left", indicator=True)

    # PersonNumber dalla colonna dell'anagrafica (qualsiasi nome inizi con "Person")
    pnum_col = next(
        (c for c in df_pers.columns if c.lower().startswith("person")), None
    )

    df_join["PersonNumber"] = df_join.apply(
        lambda r: r[pnum_col]
        if pnum_col and r["_merge"] == "both" and r[pnum_col]
        else "Nessun dipendente",
        axis=1,
    )
    df_bad["PersonNumber"] = "Nessun dipendente"

    # ---------- DOCUMENT TYPE / COUNTRY ----------
    def _doc_type(row):
        return (
            row[cluster_col]
            if row["PersonNumber"] != "Nessun dipendente"
            else "SCARTATO"
        )

    df_join["DocumentType"] = df_join.apply(_doc_type, axis=1)
    df_bad["DocumentType"] = "SCARTATO"

    if country_col in df_ext.columns:
        df_join["Country"] = df_join.apply(
            lambda r: r[country_col]
            if r["PersonNumber"] != "Nessun dipendente"
            else "",
            axis=1,
        )
    else:
        df_join["Country"] = ""
    df_bad["Country"] = ""

    # ---------- OTHER COLUMNS ----------
    df_join["DocumentName"] = df_join.apply(
        lambda r: f"{r['Nome']} {r['Cognome']}"
        if r["PersonNumber"] != "Nessun dipendente"
        else "Nessun dipendente",
        axis=1,
    )
    df_bad["DocumentName"] = "Nessun dipendente"

    df_join["DateFrom"] = df_join["Data"]
    df_bad["DateFrom"] = df_bad["Data"]

    # DocumentCode
    def _code(r):
        if (
            r["PersonNumber"] == "Nessun dipendente"
            or _is_ph(r["DateFrom"], {"NODATE", "ERRORE"})
            or r["DocumentType"] == "SCARTATO"
        ):
            return ""
        return f"{r['PersonNumber']}_{r['DateFrom'].replace('/','')}_{r['DocumentType'].replace(' ', '_')}"

    df_join["DocumentCode"] = df_join.apply(_code, axis=1)
    df_bad["DocumentCode"] = ""

    # fixed columns
    for frame in (df_join, df_bad):
        frame["METADATA"] = "MERGE"
        frame["DocumentsOfRecord"] = "DocumentsOfRecord"
        frame["DateTo"] = ""
        frame["SourceSystemOwner"] = "PEOPLE"
        frame["SourceSystemId"] = frame["DocumentCode"]

    # ---------- UNION & SELECT ORDER ----------
    final = pd.concat([df_join, df_bad], ignore_index=True, sort=False)

    final = final.rename(columns={"File_Name": "FILENAME"})  # se diverso, adatta qui
    ordered_cols = [
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
    final = final[ordered_cols]

    # ---------- SAVE ----------
    out_path = Path(out_path)
    final.to_csv(out_path, index=False, sep="|")
    print(f"✓ CSV creato → {out_path.resolve()}  righe: {len(final)}")

    return final


def run_etl(df_results, config):
    """
    Legacy function for backward compatibility.
    Now uses the new build_final_csv function.
    """
    # Save the extracted results to a temporary CSV
    temp_extracted_path = "tmp/extracted_results.csv"
    df_results.to_csv(temp_extracted_path, index=False)

    # Get the paths for the reference files
    personale_path = f"data/Elenco Personale.xlsx - Foglio 1.csv"
    cluster_path = f"data/Cluster Docs.xlsx - Foglio1.csv"

    # Load cluster data to get DocumentType and Country mapping
    df_cluster = read_csv_from_gcs(
        "Cluster Docs.xlsx - Foglio1.csv", config["INPUT_BUCKET"], "data/"
    )

    # Merge cluster data with extracted results to get DocumentType and Country
    df_with_cluster = pd.merge(df_results, df_cluster, on="Cluster", how="left")
    df_with_cluster.to_csv(temp_extracted_path, index=False)

    # Use the new build_final_csv function
    return build_final_csv(
        extracted_csv=temp_extracted_path,
        personale_csv=personale_path,
        out_path="final_documents.csv",
        cluster_col="Document Type HCM",
        country_col="Country Document HCM",
    )
