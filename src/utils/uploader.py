from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from src.config.logging import logger
from src.config.setup import config
from google.cloud import storage
from pathlib import Path
from typing import Union


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
        raise


def upload_to_gcs(client: storage.Client, source_file: Union[str, Path], destination_blob_name: str) -> None:
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
    except Exception as e:
        logger.error(f"Failed to upload {source_file} to GCS: {e}")


def upload(pdf_folder: Union[str, Path]) -> None:
    """
    Main function to iterate over PDFs and upload them to GCS.

    Args:
        pdf_folder (Union[str, Path]): Path to the folder containing PDFs.
    """
    client = initialize_gcs_client()

    for pdf_file in Path(pdf_folder).glob("*.pdf"):
        destination_blob_name = pdf_file.name
        upload_to_gcs(client, pdf_file, destination_blob_name)
    logger.info("All PDFs uploaded successfully!")


if __name__ == "__main__":
    upload("./data/pdfs")
