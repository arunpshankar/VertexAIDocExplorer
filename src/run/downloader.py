from src.utils.downloader import download
from pathlib import Path
import asyncio


if __name__ == "__main__":
    jsonl_path = Path("./data/site-search-results-pruned.jsonl")
    output_folder = Path("./data/pdfs")

    # Run the main coroutine using an asyncio event loop
    asyncio.run(download(jsonl_path, output_folder))