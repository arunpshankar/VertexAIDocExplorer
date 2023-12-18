from aiofiles import open as aio_open
import jsonlines
import aiohttp
import asyncio


async def download_file(session, url, destination):
    """
    Asynchronously downloads a file from a given URL and saves it to the specified destination.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        url (str): The URL of the file to download.
        destination (Path): The path where the file should be saved.

    Returns:
        str: The path of the downloaded file.
    """
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to download {url}. Status code: {response.status}")
            return None

        # Open the destination file in binary write mode
        async with aio_open(destination, 'wb') as f:
            await f.write(await response.read())

    return destination

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
                print(item)
                title = sanitize_filename(item["title"]) + ".pdf"
                destination = output_folder / title
                tasks.append(download_file(session, item["link"], destination))
        
        # Gather all the download tasks and execute them concurrently
        await asyncio.gather(*tasks)


async def download_from_txt(txt_path, output_folder):
    """
    Reads URLs from a text file and downloads each as a PDF file.

    Args:
        txt_path (Path): Path to the text file containing URLs.
        output_folder (Path): Folder to save the downloaded PDFs.
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Open and read the text file
        async with aio_open(txt_path, 'r') as file:
            async for line in file:
                url = line.strip()
                if url:
                    # Extract filename from URL
                    filename = url.split('/')[-1]
                    sanitized_filename = sanitize_filename(filename)
                    destination = output_folder / sanitized_filename
                    tasks.append(download_file(session, url, destination))

        # Execute all download tasks concurrently
        await asyncio.gather(*tasks)
