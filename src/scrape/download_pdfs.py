import os
from pathlib import Path
import asyncio
from src.utils.downloader import download_from_txt

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the txt file
    jsonl_path = Path(script_dir, "pdf_urls.txt")
    print(f"Absolute path to the txt file: {jsonl_path}")

    # Construct the absolute path to the output folder
    output_folder = Path(script_dir, "pdf_files")

    # Create the output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # Run the main coroutine using an asyncio event loop
    asyncio.run(download_from_txt(jsonl_path, output_folder))
