import google.generativeai as genai
from google.cloud import documentai_v1 as documentai
from langchain.chat_models.base import BaseChatModel
from langchain.schema import AIMessage, HumanMessage


class GeminiChatModel(BaseChatModel):
    def __init__(self, model_name: str, api_key: str):
        self.model = genai.GenerativeModel(model_name=model_name)
        genai.configure(api_key=api_key)

    def _generate(self, messages, stop=None):
        prompt = "\n".join([m.content for m in messages if isinstance(m, HumanMessage)])
        response = self.model.generate_content(prompt)
        return AIMessage(content=response.text)


# Usage:
llm = GeminiChatModel(model_name="gemini-pro", api_key="your_api_key")

# Now you can plug this into LangGraph as a node.


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
    raw_document = documentai.RawDocument(
        content=image_content, mime_type="image/tiff"
    )  # Adjust mime_type as needed

    # Configure the ProcessRequest
    request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)

    # Call the Document AI API
    result = document_ai_client.process_document(request=request)

    # Get the Document object from the response
    document = result.document

    print(f"Document Text:\n{document.text}\n")

    # Example: Accessing entities (if your processor extracts them)
    if document.entities:
        print("Extracted Entities:")
        for entity in document.entities:
            print(f"  Type: {entity.type_}, Mention Text: {entity.mention_text}")

    return document.pages

    """for page in document.pages:
        for form_field in page.form_fields:
            field_name = form_field.field_name.text_anchor.content if form_field.field_name.text_anchor else "N/A"
            field_value = form_field.field_value.text_anchor.content if form_field.field_value.text_anchor else "N/A"
            print(f"  Field Name: {field_name}, Value: {field_value}")"""


def process_documents():
    print("Processing documents")
    return "Ciao"
