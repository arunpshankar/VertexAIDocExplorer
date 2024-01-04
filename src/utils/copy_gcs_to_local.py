from google.api_core.exceptions import GoogleAPICallError
from google.api_core.exceptions import RetryError
from src.config.logging import logger
from src.config.setup import config
from google.cloud import storage
import time
import os 


def download_pdfs_from_gcs(bucket_name, local_folder):
    """Downloads all PDF files from a GCS bucket to a local folder."""

    def download_blob(blob, destination_file_name, retries=0):
        """Attempt to download a blob with retry mechanism."""
        max_retries = 3
        try:
            blob.download_to_filename(destination_file_name)
            logger.info(f"Blob {blob.name} downloaded to {destination_file_name}.")
        except (GoogleAPICallError, RetryError) as e:
            if retries < max_retries:
                time.sleep(2 ** retries)  # Exponential backoff
                download_blob(blob, destination_file_name, retries + 1)
            else:
                logger.error(f"Failed to download {blob.name} after {max_retries} retries.")

    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    for blob in blobs:
        if blob.name.lower().endswith('.pdf'):
            destination_file_name = os.path.join(local_folder, os.path.basename(blob.name))
            download_blob(blob, destination_file_name)

# Example usage
bucket_url = "moodys-demo-doc-search"  # Replace with your GCS bucket name
local_data_folder = "./src/utils/pdfs"      # Replace with your local folder path
download_pdfs_from_gcs(bucket_url, local_data_folder)
