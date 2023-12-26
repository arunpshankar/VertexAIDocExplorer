from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from src.config.logging import logger
from urllib.parse import urlparse
from urllib.parse import urljoin
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Tuple
from typing import List
from typing import Set
import asyncio
import time 
import csv


class PDFScraper:
    def __init__(self, webdriver_path: str):
        self.webdriver_path = webdriver_path

    def _initialize_webdriver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(self.webdriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def _scrape_urls_from_page_sync(self, url: str) -> List[str]:
        driver = self._initialize_webdriver()
        try:
            logger.info(f"Opening the webpage: {url}")
            driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            a_tags = soup.find_all('a', href=True)
            urls = [tag['href'] for tag in a_tags]
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            urls = []
        finally:
            driver.quit()
        return urls

    def scrape_pdf_urls_sync(self, base_url: str) -> Set[str]:
        unique_pdf_urls = set()
        non_pdf_urls = set()
        urls = self._scrape_urls_from_page_sync(base_url)
        root_domain = extract_root_domain(base_url)

        for url in urls:
            if url.endswith(".pdf") and not "inline" in url:
                unique_pdf_urls.add(url)
            elif ".pdf" in url and 'inline' in url:
                pdf_url = url.split('?')[0]
                unique_pdf_urls.add(pdf_url)
            elif ".pdf" not in url and url.startswith("http"):
                domain = extract_root_domain(url)
                if domain == root_domain:
                    non_pdf_urls.add(url)
        """
        for non_pdf_url in non_pdf_urls:
            urls = self._scrape_urls_from_page_sync(non_pdf_url)
            for url in urls:
                if url.endswith(".pdf") and not "inline" in url:
                    unique_pdf_urls.add(url)
                elif ".pdf" in url and 'inline' in url:
                    pdf_url = url.split('?')[0]
                    unique_pdf_urls.add(pdf_url)
        """

        return unique_pdf_urls


def extract_root_domain(url: str) -> str:
    """
    Extracts and returns the root domain from a given URL.

    Parameters:
    url (str): The URL from which the root domain needs to be extracted.

    Returns:
    str: The root domain of the URL. Returns '' if the URL is invalid.
    """
    try:
        parsed_url = urlparse(url)
        root_domain = parsed_url.netloc.split(':')[0]
        return f'https://{root_domain}'
    except Exception as e:
        logger.error(f"Error extracting domain: {e}")
        return ''

def resolve_pdf_url(base_url: str, pdf_url: str) -> str:
    """
    Resolve a PDF URL to a full URL using the base URL's root domain. 
    Handles various forms of relative URLs.

    Args:
    base_url (str): The base URL.
    pdf_url (str): The relative or full URL to the PDF.

    Returns:
    str: The full URL to the PDF, or an empty string if invalid.
    """
    # Extract the root domain from the base URL
    root_domain = extract_root_domain(base_url)
    
    if not root_domain:
        logger.error("Invalid base URL")
        return ''

    # Check if the PDF URL is already a full URL
    if pdf_url.lower().startswith('http://') or pdf_url.lower().startswith('https://'):
        return pdf_url

    # Use urljoin to handle relative URLs like '../../' and '../'
    full_pdf_url = urljoin(root_domain, pdf_url)

    # Validate the resolved URL
    try:
        parsed_url = urlparse(full_pdf_url)
        if parsed_url.scheme and parsed_url.netloc:
            return full_pdf_url
        else:
            logger.error("Resolved URL is invalid")
            return ''
    except Exception as e:
        logger.error(f"Error resolving PDF URL: {e}")
        return ''

# Asynchronous wrappers for the synchronous methods
async def scrape_urls_from_page_async(scraper, url, executor):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, scraper._scrape_urls_from_page_sync, url)


async def scrape_pdf_urls_async(scraper, base_url, executor):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, scraper.scrape_pdf_urls_sync, base_url)


# Asynchronous file operations (can be adapted to use aiofiles if needed)
async def read_input_csv_async(file_path: str) -> List[Tuple[str, str]]:
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header row
        data = [(row[0], row[1]) for row in reader]
    return data


async def write_output_csv_async(file_path: str, data: List[Tuple[str, str, str, str]]):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['bank', 'base_url', 'pdf_url', 'resolved_pdf_url'])
        for row in data:
            writer.writerow(row)

# Main asynchronous scraping function
async def scrape_to_file_async(input_file_path: str, webdriver_path: str, output_file_path: str):
    scraper = PDFScraper(webdriver_path)
    input_data = await read_input_csv_async(input_file_path)
    output_data = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        tasks = [scrape_pdf_urls_async(scraper, base_url, executor) for _, base_url in input_data]
        results = await asyncio.gather(*tasks)

        for (bank, base_url), pdf_urls in zip(input_data, results):
            for pdf_url in pdf_urls:
                resolved_pdf_url = resolve_pdf_url(base_url, pdf_url)
                output_data.append((bank, base_url, pdf_url, resolved_pdf_url))

    await write_output_csv_async(output_file_path, output_data)

# Entry point
if __name__ == '__main__':
    asyncio.run(scrape_to_file_async(
        input_file_path='./src/scrape/input_urls.csv',
        webdriver_path='./src/scrape/chromedriver',
        output_file_path='./src/scrape/pdf_urls.csv'
    ))
