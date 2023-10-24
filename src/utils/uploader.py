from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.cloud import storage
from pathlib import Path


PROJECT_ID = 'arun-genai-bb'

def initialize_gcs_client(credentials_path):
    """
    Initialize the Google Cloud Storage client using provided service account credentials.

    Args:
        credentials_path (Path): Path to the service account credentials (JSON) file.

    Returns:
        google.cloud.storage.client.Client: Initialized GCS client.
    """
    credentials = ServiceAccountCredentials.from_service_account_file(credentials_path)
    return storage.Client(credentials=credentials, project=PROJECT_ID)


def upload_to_gcs(client, bucket_name, source_file, destination_blob_name):
    """
    Uploads a file to the specified GCS bucket.

    Args:
        client (google.cloud.storage.client.Client): Initialized GCS client.
        bucket_name (str): Name of the GCS bucket.
        source_file (Path): Path to the file to be uploaded.
        destination_blob_name (str): Desired blob name in the GCS bucket.
    """
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)

def main(pdf_folder, bucket_name, credentials_path):
    """
    Main function to iterate over PDFs and upload them to GCS.

    Args:
        pdf_folder (Path): Path to the folder containing PDFs.
        bucket_name (str): Name of the GCS bucket.
        credentials_path (Path): Path to the service account credentials (JSON) file.
    """
    client = initialize_gcs_client(credentials_path)

    for pdf_file in pdf_folder.glob("*.pdf"):
        destination_blob_name = pdf_file.name
        upload_to_gcs(client, bucket_name, pdf_file, destination_blob_name)
        print(f"Uploaded {pdf_file.name} to {bucket_name}/{destination_blob_name}")

if __name__ == "__main__":
    pdf_folder = Path("./data/pdfs")
    bucket_name = "fin-pdfs"
    credentials_path = Path("./credentials/vai-key.json")
    main(pdf_folder, bucket_name, credentials_path)
