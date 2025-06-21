import json

import pandas as pd
import vertexai
from google.cloud import storage
from vertexai.preview.generative_models import GenerativeModel, Part

auth.authenticate_user()

PROJECT_ID = "credemhack-cloudfunctions"
LOCATION = "europe-west4"
GCS_BUCKET_NAME = "credemhack_cloud_fuctions"
GCS_INPUT_PREFIX = "input/"
GCS_DATA_PREFIX = "data/"

vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.0-flash-001")
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.get_bucket(GCS_BUCKET_NAME)


def process_document_with_ai(name, content):
    mime = get_mime_type(name)
    if mime == "application/octet-stream":
        return {k: "Unsupported Type" for k in ["Nome", "Cognome", "Data", "Cluster"]}
    try:
        part = Part.from_data(data=content, mime_type=mime)
        prompt = """
    Classifica ogni documento fornito, che può essere in formato TIFF, PDF o altri formati di immagine, assegnandolo a uno dei seguenti cluster specifici:

        Provvedimenti a favore, Supervisione Mifid, Flessibilità orarie, Polizza sanitaria, Formazione, Fringe benefits, Assunzione matricola, Primo impiego, Fondo pensione, Nulla osta assunzione, Destinazione TFR, Nomina titolarità, Assegnazione ruolo, Part-time, Cessazione, Proroga TD, Provvedimenti disciplinari, Trasferimento, Lettera assunzione, Titolarità temporanee, Trasformazione TI, Proposta di assunzione. Se non sei sicuro al 100% della categoria, assegna "Nessun cluster".

        Estrai inoltre da ogni documento i seguenti dati chiave: Nome, Cognome e Data (intesa come la data di redazione presente nel documento).

        Procedi in modo accurato e dettagliato, analizzando il contenuto dei documenti per supportare la classificazione e l'estrazione delle informazioni.

        # Steps

        1. Analizza il contenuto del documento fornito (TIFF, PDF o altro formato immagine).
        2. Identifica ed estrai con precisione Nome, Cognome e la Data di redazione dal testo.
        3. Valuta il documento per determinarne la classificazione, confrontandolo con i cluster elencati.
        4. Se la corrispondenza con un cluster è incerta, assegna "Nessun cluster".

        # Output Format

        Restituisci solo una risposta strutturata in JSON con i seguenti campi, senza commenti o spiegazioni aggiuntive:
        ```json
        {{
          "Nome": "[Nome estratto]",
          "Cognome": "[Cognome estratto]",
          "Data": "[Data estratta in formato ISO 8601, es.YYYY-MM-DD o 'Non Trovata']",
          "Cluster": "[Nome cluster assegnato o 'Nessun cluster']"
        }}
        ```
    """
        res = model.generate_content([part, prompt])
        return parse_json_response(res.text, name)
    except:
        return {k: "Error" for k in ["Nome", "Cognome", "Data", "Cluster"]}


def process_gcs_documents():
    exts = (".pdf", ".tif", ".tiff", ".png", ".jpeg", ".jpg")
    blobs = [
        b
        for b in bucket.list_blobs(prefix=GCS_INPUT_PREFIX)
        if b.name.lower().endswith(exts)
    ]
    results = []
    for blob in blobs:
        try:
            content = blob.download_as_bytes()
            info = process_document_with_ai(blob.name, content)
            info["File Name"] = blob.name
            results.append(info)
        except Exception as e:  # Catch specific exception for better debugging
            results.append(
                {
                    "File Name": blob.name,
                    **{
                        k: f"Download Error: {e}"
                        for k in ["Nome", "Cognome", "Data", "Cluster"]
                    },
                }
            )
    return pd.DataFrame(results)


def read_csv_from_gcs(name):
    return pd.read_csv(f"gs://{GCS_BUCKET_NAME}/{GCS_DATA_PREFIX}{name}")


def run_pipeline():
    df_results = process_gcs_documents()
    if df_results.empty:
        print("No documents processed or found.")
        return pd.DataFrame()

    # Ensure columns exist before attempting to convert or merge
    if "Nome" in df_results.columns:
        df_results["Nome"] = df_results["Nome"].astype(str).str.lower()
    else:
        df_results["Nome"] = "Error"  # Handle missing column case

    if "Cognome" in df_results.columns:
        df_results["Cognome"] = df_results["Cognome"].astype(str).str.lower()
    else:
        df_results["Cognome"] = "Error"  # Handle missing column case

    df_cluster = read_csv_from_gcs("cluster.csv")
    df_personale = read_csv_from_gcs("elenco_personale.csv")

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


# Esecuzione
df_final = run_pipeline()
