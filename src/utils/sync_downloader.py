from src.config.logging import logger
from pathlib import Path
import jsonlines
import requests
import time
import csv


def download_file(url, destination, max_retries=3, timeout_duration=10):
    """
    Synchronously downloads a file from a given URL and saves it to the specified destination. 
    Implements retry logic with quick retries for certain connection errors.

    Args:
        url (str): The URL of the file to download.
        destination (Path): The path where the file should be saved.
        max_retries (int): Maximum number of retries for the download.
        timeout_duration (int): The total timeout duration for each attempt in seconds.

    Returns:
        str: The path of the downloaded file, or None if the download fails.
    """
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url, timeout=timeout_duration)
            if response.status_code == 200:
                with open(destination, 'wb') as f:
                    f.write(response.content)
                return destination
            else:
                logger.info(f"Failed to download {url}. Status code: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Quick retry {retries + 1}/{max_retries} for {url} due to connection error.")
            time.sleep(1)  # Short delay for quick retries
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            logger.error(f"Retry {retries + 1}/{max_retries} for {url}. Error: {type(e).__name__}")
            time.sleep(1)  # Delay for other errors
        except Exception as e:
            logger.error(type(e).__name__)


        retries += 1

    print(f"Failed to download {url} after {max_retries} retries.")
    return None

def sanitize_filename(filename):
    """
    Sanitizes the filename to ensure it's valid.

    Args:
        filename (str): The original filename.

    Returns:
        str: A sanitized version of the filename.
    """
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '.', '_')]).rstrip()

def download_from_jsonl(jsonl_path, output_folder):
    """
    Reads a JSONL file and downloads each file listed in it.

    Args:
        jsonl_path (Path): Path to the JSONL file.
        output_folder (Path): Folder to save the downloaded files.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    with jsonlines.open(jsonl_path) as reader:
        for item in reader:
            title = sanitize_filename(item["title"]) + ".pdf"
            destination = output_folder / title
            download_file(item["link"], destination)

def download_from_csv(csv_path, output_folder):
    """
    Reads URLs from a CSV file and downloads each as a file.
    The CSV file should have a column named 'resolved_pdf_url' containing the URLs.

    Args:
        csv_path (Path): Path to the CSV file containing URLs.
        output_folder (Path): Folder to save the downloaded files.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    with open(csv_path, 'r', newline='') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            url = row.get('resolved_pdf_url', '').strip()
            bank_name = row.get('bank', '').strip()
            output_path = Path(f'{output_folder}/{bank_name}')
            output_path.mkdir(parents=True, exist_ok=True)
            if url:
                filename = url.split('/')[-1]
                sanitized_filename = sanitize_filename(filename)
                destination = f'{output_path}/{sanitized_filename}'
                logger.info(f'Downloading PDF from: {url}')
                download_file(url, destination)
