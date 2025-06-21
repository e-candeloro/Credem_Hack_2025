import os
from collections import namedtuple
from datetime import datetime
from typing import Any, Dict, Optional

import google.generativeai as genai
import pandas as pd
from google.cloud import documentai_v1 as documentai
from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from tqdm import tqdm
from utils.file_formatting import get_mime_type
from utils.parsing import parse_json_response
from utils.reading import load_file_as_bytes
from vertexai.preview.generative_models import GenerativeModel, Part


class DocumentField(BaseModel):
    """Represents a single field extracted from a document."""

    field_name: str = Field(..., description="Name of the extracted field")
    field_value: str = Field(..., description="Value of the extracted field")


class ProcessedDocument(BaseModel):
    """Represents a processed document with extracted data."""

    filename: str = Field(..., description="Name of the processed file")
    fields: dict[str, str] = Field(
        default_factory=dict, description="Extracted field-value pairs"
    )


class DocumentProcessingResult(BaseModel):
    """Container for multiple processed documents."""

    documents: dict[str, ProcessedDocument] = Field(
        default_factory=dict, description="Filename to processed document mapping"
    )
    total_processed: int = Field(
        default=0, description="Total number of documents processed"
    )
    processing_time: float | None = Field(
        default=None, description="Total processing time in seconds"
    )

    def add_document(self, filename: str, document: ProcessedDocument):
        """Add a processed document to the result."""
        self.documents[filename] = document
        self.total_processed += 1


def process_document_docAI(
    project_id: str, location: str, processor_id: str, file_path: str
):
    """Processes a document using Document AI."""

    document_ai_client = documentai.DocumentProcessorServiceClient()
    processor_name = document_ai_client.processor_path(
        project_id, location, processor_id
    )
    # Read the file into memory
    with open(file_path, "rb") as image_file:
        image_content = image_file.read()

    # Create a RawDocument object
    mime_type = get_mime_type(file_path)
    raw_document = documentai.RawDocument(
        content=image_content, mime_type=mime_type
    )  # Adjust mime_type as needed

    # Configure the ProcessRequest
    request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)

    # Call the Document AI API
    result = document_ai_client.process_document(request=request)

    # Get the Document object from the response
    document = result.document

    # Example: Accessing entities (if your processor extracts them)
    if document.entities:
        print("Extracted Entities:")
        for entity in document.entities:
            print(f"  Type: {entity.type_}, Mention Text: {entity.mention_text}")

    return document.text


def process_documents_docAI(config, tmp_folder: str = "tmp/"):
    """
    Process all documents in the tmp/ folder using Document AI.


    Returns:
        DocumentProcessingResult containing all processed documents
    """

    project_id: str = config["PROJECT_ID"]
    location: str = config["LOCATION"]
    processor_id: str = config["PROCESSOR_ID"]

    result = []

    # Check if tmp folder exists
    if not os.path.exists(tmp_folder):
        print(f"Warning: {tmp_folder} directory does not exist")
        return result

    # Get list of files in tmp folder
    try:
        files = [
            f
            for f in os.listdir(tmp_folder)
            if os.path.isfile(os.path.join(tmp_folder, f))
        ]
    except PermissionError:
        print(f"Error: Permission denied accessing {tmp_folder}")
        return result

    if not files:
        print(f"No files found in {tmp_folder}")
        return result

    print(f"Found {len(files)} files to process")

    # Process each file
    for index, filename in tqdm(enumerate(files)):
        if filename.endswith(".csv"):
            continue
        try:
            # Process document with Document AI
            extracted_fields = process_document_docAI(
                project_id=project_id,
                location=location,
                processor_id=processor_id,
                file_path=os.path.join(tmp_folder, filename),
            )

            # Create ProcessedDocument instance
            processed_doc = namedtuple("ProcessedDocument", ["filename", "fields"])(
                filename, extracted_fields
            )

            # Add to result
            result.append(processed_doc)

        except Exception as e:
            processed_doc = namedtuple("ProcessedDocument", ["filename", "fields"])(
                filename,
                "Nome, cognome e data non trovati. Metti ERRORE in tutti i campi",
            )

    return result


def process_document_with_gemini(name, content):
    model = GenerativeModel("gemini-2.0-flash-001")
    mime = get_mime_type(name)
    if mime == "application/octet-stream":
        return {
            k: "Unsupported Type"
            for k in ["File Name", "Nome", "Cognome", "Data", "Cluster"]
        }
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
            "File Name": "[Nome del file]",
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
        return {k: "Error" for k in ["File Name", "Nome", "Cognome", "Data", "Cluster"]}


def all_process_documents_docAI_gemini(config, tmp_folder: str = "tmp/"):
    model = GenerativeModel("gemini-2.0-flash-001")
    docs = process_documents_docAI(config, tmp_folder)
    results = []
    for index, (filename, document) in enumerate(docs):
        part = "FILENAME: " + filename + "\n" + "CONTENT: " + str(document)
        prompt = """
        Classifica ogni documento fornito, che ti verrà fornito sotto forma di testo, assegnandolo a uno dei seguenti cluster specifici:

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
        results.append(parse_json_response(res.text, filename))
    return pd.DataFrame(results)


def all_process_documents_gemini(config, tmp_folder: str = "tmp/"):
    if not os.path.exists(tmp_folder):
        raise ValueError(f"Warning: {tmp_folder} directory does not exist")

    # Get list of files in tmp folder
    try:
        files = [
            f
            for f in os.listdir(tmp_folder)
            if os.path.isfile(os.path.join(tmp_folder, f))
        ]
    except PermissionError:
        print(f"Error: Permission denied accessing {tmp_folder}")
        return ""

    if not files:
        print(f"No files found in {tmp_folder}")
        return ""

    print(f"Found {len(files)} files to process")
    results = []
    # Process each file
    for filename in files:
        file_path = os.path.join(tmp_folder, filename)

        try:
            content = load_file_as_bytes(file_path)
            info = process_document_with_gemini(filename, content)
            info["File Name"] = filename
            results.append(info)
        except Exception as e:  # Catch specific exception for better debugging
            results.append(
                {
                    "File Name": filename,
                    **{
                        k: f"Download Error: {e}"
                        for k in ["Nome", "Cognome", "Data", "Cluster"]
                    },
                }
            )
    return pd.DataFrame(results)


def all_process_documents_OVERPOWERED(config, tmp_folder: str = "tmp/"):
    model = GenerativeModel("gemini-2.0-flash-001")
    docs = process_documents_docAI(config, tmp_folder)
    results = []
    df_cluster = pd.read_csv(config["CLUSTER_PATH"])
    cluster_classes = str(df_cluster["Cluster"].unique().tolist())
    for index, (filename, document) in tqdm(enumerate(docs)):
        byte_content = load_file_as_bytes(os.path.join(tmp_folder, filename))
        byte_part = Part.from_data(data=byte_content, mime_type=get_mime_type(filename))
        part = "FILENAME: " + filename + "\n" + "CONTENT: " + str(document)
        prompt = f"""I documenti ti verranno forniti sia in forma di byte che di testo, con anche il filename.
        Classifica ogni documento fornito, assegnandolo a uno dei seguenti cluster specifici:

            Cluster (esempi in  lista python, considera i soli valori):
            {cluster_classes}

            Estrai inoltre da ogni documento i seguenti dati chiave: Nome, Cognome, Data (intesa come la data di redazione presente nel documento) e Country (intesa come il paese di redazione del documento, nome in inglese).
            Se non è possibile estrarre il nome, il cognome o la data, restituisci "ERRORE" al posto del valore.

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
            "File_Name": "[Nome del file]",
            "Nome": "[Nome estratto]",
            "Cognome": "[Cognome estratto]",
            "Data": "[Data estratta in formato ISO 8601, es.YYYY-MM-DD o 'ERRORE']",
            "Cluster": "[Nome cluster assegnato o 'Nessun cluster']",
            "Country": "[Paese di redazione del documento, nome in inglese o 'ERRORE']"
            }}

            ```
            Esempio:
            ```json
            {{
            "File_Name": "nome_file.pdf",
            "Nome": "Mario",
            "Cognome": "ERRORE",
            "Data": "2002-01-04",
            "Cluster": "Nessun cluster",
            "Country": "Italy"
            }}
        """
        res = model.generate_content([part, prompt, byte_part])
        results.append(parse_json_response(res.text, filename))
    return pd.DataFrame(results)
