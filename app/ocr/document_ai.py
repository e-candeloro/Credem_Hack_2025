import os
from datetime import datetime
from typing import Any, Dict, Optional

import google.generativeai as genai
from google.cloud import documentai_v1 as documentai
from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage, HumanMessage
from pydantic import BaseModel, Field


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


def process_document_with_docai(
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
    if file_path.lower().endswith(".tiff") or file_path.lower().endswith(".tif"):
        mime_type = "image/tiff"
    elif file_path.lower().endswith(".pdf"):
        mime_type = "application/pdf"
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
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

    document_dict = {}
    for page in document.pages:
        for form_field in page.form_fields:
            field_name = (
                form_field.field_name.text_anchor.content
                if form_field.field_name.text_anchor
                else "N/A"
            )
            field_value = (
                form_field.field_value.text_anchor.content
                if form_field.field_value.text_anchor
                else "N/A"
            )
            document_dict[field_name] = field_value
    return document_dict


def process_documents(config, tmp_folder: str = "tmp/") -> DocumentProcessingResult:
    """
    Process all documents in the tmp/ folder using Document AI.


    Returns:
        DocumentProcessingResult containing all processed documents
    """
    import time

    start_time = time.time()
    project_id: str = config["PROJECT_ID"]
    location: str = config["LOCATION"]
    processor_id: str = config["PROCESSOR_ID"]

    result = DocumentProcessingResult()

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
    for filename in files:
        file_path = os.path.join(tmp_folder, filename)
        if filename.endswith(".csv"):
            continue
        try:
            print(f"Processing {filename}...")

            # Process document with Document AI
            extracted_fields = process_document_with_docai(
                project_id=project_id,
                location=location,
                processor_id=processor_id,
                file_path=file_path,
            )

            # Create ProcessedDocument instance
            processed_doc = ProcessedDocument(
                filename=filename,
                fields=extracted_fields,
            )

            # Add to result
            result.add_document(filename, processed_doc)

            print(f"Successfully processed {filename}")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            # Create error document
            error_doc = ProcessedDocument(
                filename=filename,
                fields={"error": str(e)},
            )
            result.add_document(filename, error_doc)
            for filename in files:
                file_path = os.path.join(tmp_folder, filename)
                extracted_fields = process_document_with_docai(
                    project_id=project_id,
                    location=location,
                    processor_id=processor_id,
                    file_path=file_path,
                )

    for filename in files:
        file_path = os.path.join(tmp_folder, filename)
        extracted_fields = process_document_with_docai(
            project_id=project_id,
            location=location,
            processor_id=processor_id,
            file_path=file_path,
        )
    # Calculate processing time
    result.processing_time = time.time() - start_time

    print(
        f"Processing complete. Processed {result.total_processed} documents in {result.processing_time:.2f} seconds"
    )

    return result
