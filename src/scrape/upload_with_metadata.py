from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from src.config.logging import logger
from src.config.setup import config
from google.cloud import storage
from pathlib import Path
from typing import Union
import jsonlines
import json


def initialize_gcs_client() -> storage.Client:
    """
    Initialize the Google Cloud Storage client using provided service account credentials.

    Returns:
        google.cloud.storage.client.Client: Initialized GCS client.
    """
    try:
        credentials = ServiceAccountCredentials.from_service_account_file(config.CREDENTIALS_PATH)
        return storage.Client(credentials=credentials, project=config.PROJECT_ID)
    except Exception as e:
        logger.error(f"Failed to initialize GCS client: {e}")


def upload_to_gcs(client: storage.Client, source_file: Union[str, Path], destination_blob_name: str, writer, id_: str, company_name: str) -> None:
    """
    Uploads a file to the specified GCS bucket.

    Args:
        client (google.cloud.storage.client.Client): Initialized GCS client.
        source_file (Union[str, Path]): Path to the file to be uploaded.
        destination_blob_name (str): Desired blob name in the GCS bucket.
    """
    try:
        bucket = client.get_bucket(config.DOC_SEARCH_BUCKET)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(str(source_file))
        logger.info(f"Successfully uploaded {source_file} to {config.DOC_SEARCH_BUCKET}/{destination_blob_name}")
        uri = f'gs://{config.DOC_SEARCH_BUCKET}/{destination_blob_name}'
        json_data = json.dumps({"company": company_name})
        metadata = {"id": str(id_), "jsonData": json_data, "content": {"mimeType": "application/pdf", "uri": uri}}
        writer.write(metadata)
    except Exception as e:
        logger.error(f"Failed to upload {source_file} to GCS: {e}")

def extract_company_name(file_path: Path) -> str:
    """
    Extracts the company name from a given file path, specifically a Path object.

    The function assumes that the file path contains a segment 'pdf_files/',
    and the company name is the directory immediately following this segment.

    Parameters:
    file_path (Path): The file path (as a Path object) from which to extract the company name.

    Returns:
    str: The extracted company name.
    """
    try:
        parts = list(file_path.parts)
        company_name_index = parts.index('pdf_files') + 1
        return parts[company_name_index]
    except Exception as e:
        logger.error(e)


def upload(pdf_folder: Union[str, Path]) -> None:
    """
    Main function to iterate over PDFs in subdirectories and upload them to GCS.

    Args:
        pdf_folder (Union[str, Path]): Path to the folder containing subdirectories with PDFs.
    """
    client = initialize_gcs_client()
    metadata_file_path = './src/scrape/pdf_files/metadata.jsonl'
    writer = jsonlines.open(metadata_file_path, mode='w')

    # Use rglob to find PDFs in subdirectories
    id_ = 1
    for pdf_file in Path(pdf_folder).rglob("*.pdf"):
        destination_blob_name = pdf_file.name
        company_name = extract_company_name(pdf_file)
        upload_to_gcs(client, pdf_file, destination_blob_name, writer, id_, company_name)
        id_ += 1

    logger.info("All PDFs uploaded successfully!")
    writer.close()


def upload_json() -> None:
    """
    Uploads a JSON file to the specified GCS bucket.

    Args:
        client (google.cloud.storage.client.Client): Initialized GCS client.
        json_file_path (str): Path to the JSON file to be uploaded.
        destination_blob_name (str): Desired blob name in the GCS bucket.
    """
    try:
        # Assuming the bucket name is stored in a config variable
        client = initialize_gcs_client()
        metadata_file_path = './src/scrape/pdf_files/metadata.jsonl'
        bucket = client.get_bucket(config.DOC_SEARCH_BUCKET)
        blob = bucket.blob('metadata.jsonl')
        
        # Set the blob's content type to JSON
        blob.content_type = 'application/json'
        blob.upload_from_filename(metadata_file_path)

        logger.info(f"Successfully uploaded JSON file {metadata_file_path} to {config.DOC_SEARCH_BUCKET}/metadata.json")
    except Exception as e:
        logger.error(f"Failed to upload JSON file {metadata_file_path} to GCS: {e}")


if __name__ == '__main__':
    upload('./src/scrape/pdf_files/')
    upload_json()