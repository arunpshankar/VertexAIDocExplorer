from aiohttp import ServerDisconnectedError
from aiohttp import ClientConnectorError
from aiohttp import ClientPayloadError
from aiofiles import open as aio_open
from src.config.logging import logger
from aiohttp import ClientTimeout
from pathlib import Path
import jsonlines
import aiohttp
import asyncio
import csv


async def download_file(session, url, destination, max_retries=10, timeout_duration=10):
    """
    Asynchronously downloads a file from a given URL and saves it to the specified destination. 
    Implements retry logic with quick retries for certain connection errors.

    Args:
        session (ClientSession): The aiohttp client session.
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
            async with session.get(url, timeout=ClientTimeout(total=timeout_duration)) as response:
                if response.status == 200:
                    async with aio_open(destination, 'wb') as f:
                        await f.write(await response.read())
                    return destination
                else:
                    logger.error(f"Failed to download {url}. Status code: {response.status}")
                    return None
        except ClientConnectorError as e:
            logger.error(f"Quick retry {retries + 1}/{max_retries} for {url} due to connection error.")
            await asyncio.sleep(1)  # Short delay for quick retries
        except (asyncio.TimeoutError, ClientPayloadError, ServerDisconnectedError) as e:
            logger.error(f"Retry {retries + 1}/{max_retries} for {url}. Error: {type(e).__name__}")
            await asyncio.sleep(1)  # Delay for other errors
        except Exception as e:
            logger.error(type(e).__name__)

        retries += 1

    logger.error(f"Failed to download {url} after {max_retries} retries.")
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

async def download(jsonl_path, output_folder):
    """
    Main coroutine to read the JSONL file, download and save the PDFs.

    Args:
        jsonl_path (Path): Path to the JSONL file.
        output_folder (Path): Folder to save the downloaded PDFs.
    """
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Create a new aiohttp session
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Read the JSONL file
        with jsonlines.open(jsonl_path) as reader:
            for item in reader:
                title = sanitize_filename(item["title"]) + ".pdf"
                destination = output_folder / title
                tasks.append(download_file(session, item["link"], destination))
        
        # Gather all the download tasks and execute them concurrently
        await asyncio.gather(*tasks)


async def download_from_csv(csv_path, output_folder):
    """
    Reads URLs from a CSV file and downloads each as a PDF file.
    The CSV file should have a column named 'resolved_pdf_url' containing the URLs.

    Args:
        csv_path (Path): Path to the CSV file containing URLs.
        output_folder (Path): Folder to save the downloaded PDFs.
    """
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Open and read the CSV file
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
                    tasks.append(download_file(session, url, destination))

        # Execute all download tasks concurrently
        await asyncio.gather(*tasks)

