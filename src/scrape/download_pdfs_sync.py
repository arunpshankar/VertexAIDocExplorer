from src.utils.sync_downloader import download_from_csv
from src.config.logging import logger
from pathlib import Path
import os


if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to the CSV file
    csv_path = Path(script_dir, "pdf_urls.csv")
    logger.info(f"Absolute path to the txt file: {csv_path}")

    # Construct the absolute path to the output folder
    output_folder = Path(script_dir, "pdf_files")

    # Create the output folder if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)

    # Run the main function to synchronously download the PDF files one by one
    download_from_csv(csv_path, output_folder)
