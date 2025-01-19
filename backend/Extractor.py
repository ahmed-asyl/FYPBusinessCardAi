import io
import os
from PIL import Image
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv


def analyze_business_card(file):
    """
    Analyzes a business card image file using Azure Form Recognizer and extracts contact details.

    Parameters:
         file (werkzeug.datastructures.FileStorage): The file object from Flask's request.files.

    Returns:
        dict: A dictionary containing the extracted contact details.
    """

    # Open the file as an image using PIL
    image = Image.open(io.BytesIO(file))

    # Create a byte stream
    byte_stream = io.BytesIO()

    # Save the image to the byte stream
    image.save(byte_stream, format='JPEG')

    # Get the byte data
    byte_data = byte_stream.getvalue()

    # Load Azure credentials from environment variables
    load_dotenv()
    endpoint = os.getenv('AZURE_ENDPOINT')
    key = os.getenv('AZURE_KEY')

    model_id = "businesscardmodel"

    # Initialize the DocumentAnalysisClient
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Analyze the document
    poller = document_analysis_client.begin_analyze_document(model_id, byte_data)
    result = poller.result()

    # Extract contact details
    contact_details = {}
    for document in result.documents:
        for name, field in document.fields.items():
            if field.value:  # Ignore None values
                contact_details[name] = field.value

    return contact_details


def business_card_confidence(file):
    """
    Analyzes a business card image file using Azure Form Recognizer and extracts the confidence score.

    Parameters:
         file (werkzeug.datastructures.FileStorage): The file object from Flask's request.files.

    Returns:
        float: The confidence score of the analysis.
    """

    # Open the file as an image using PIL
    image = Image.open(io.BytesIO(file))

    # Create a byte stream
    byte_stream = io.BytesIO()

    # Save the image to the byte stream
    image.save(byte_stream, format='JPEG')

    # Get the byte data
    byte_data = byte_stream.getvalue()

    # Load Azure credentials from environment variables
    load_dotenv()
    endpoint = os.getenv('AZURE_ENDPOINT')
    key = os.getenv('AZURE_KEY')

    model_id = "businesscardmodel"

    # Initialize the DocumentAnalysisClient
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    # Analyze the document
    poller = document_analysis_client.begin_analyze_document(model_id, byte_data)
    result = poller.result()

    # Extract contact details
    contact_confidence = {}
    for document in result.documents:
        for name, field in document.fields.items():
            if field.value:  # Ignore None values
                contact_confidence[name] = field.value, field.confidence

    return contact_confidence
