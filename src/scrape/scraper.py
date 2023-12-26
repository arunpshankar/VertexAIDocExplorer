from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from src.config.logging import logger
from urllib.parse import urlparse
from urllib.parse import urljoin
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Tuple
from typing import List
from typing import Set
import time
import csv 

class PDFScraper:
    """
    A class to scrape PDF URLs from webpages.
    """

    def __init__(self, webdriver_path: str):
        """
        Initializes the PDFScraper with a path to the Chrome WebDriver.

        Args:
        webdriver_path (str): The path to the Chrome WebDriver executable.
        """
        self.webdriver_path = webdriver_path

    def _initialize_webdriver(self) -> webdriver.Chrome:
        """
        Initializes and returns a Chrome WebDriver.

        Returns:
        webdriver.Chrome: The initialized Chrome WebDriver.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(self.webdriver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def _scrape_urls_from_page(self, url: str) -> List[str]:
        """
        Scrape all URLs from a given webpage.

        Args:
        url (str): The URL of the webpage to scrape.

        Returns:
        List[str]: A list of found URLs.
        """
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

    def scrape_pdf_urls(self, base_url: str) -> Set[str]:
        """
        Scrape all PDF URLs from a given base URL.

        Args:
        base_url (str): The base URL to start scraping from.

        Returns:
        Set[str]: A set of unique PDF URLs.
        """
        unique_pdf_urls = set()
        non_pdf_urls = set()
        urls = self._scrape_urls_from_page(base_url)
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

        # Perform one more hop of scraping
        for non_pdf_url in non_pdf_urls:
            urls = self._scrape_urls_from_page(non_pdf_url)
            for url in urls:
                if url.endswith(".pdf") and not "inline" in url:
                    unique_pdf_urls.add(url)
                elif ".pdf" in url and 'inline' in url:
                    pdf_url = url.split('?')[0]
                    unique_pdf_urls.add(pdf_url)

        return unique_pdf_urls


def read_input_csv(file_path: str) -> List[Tuple[str, str]]:
    """
    Reads a CSV file and returns a list of tuples containing bank name and URL.

    Args:
        file_path (str): Path to the input CSV file.

    Returns:
        List[Tuple[str, str]]: A list of tuples with bank name and URL.
    """
    data = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header row
        for row in reader:
            data.append((row[0], row[1]))
    return data


def write_output_csv(file_path: str, data: List[Tuple[str, str]]):
    """
    Writes the output to a CSV file.

    Args:
        file_path (str): Path to the output CSV file.
        data (List[Tuple[str, str]]): Data to be written to the CSV file.
    """
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['bank', 'base_url', 'pdf_url', 'resolved_pdf_url'])
        for row in data:
            writer.writerow(row)


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


def scrape_to_file(input_file_path: str, webdriver_path: str, output_file_path: str):
    """
    Scrape PDF URLs from base URLs in a CSV file and save them to another CSV file.

    Args:
        input_file_path (str): Path to input CSV file with bank names and base URLs.
        webdriver_path (str): Path to the Chrome WebDriver.
        output_file_path (str): Path to save the output CSV file.
    """
    scraper = PDFScraper(webdriver_path)
    input_data = read_input_csv(input_file_path)
    output_data = []

    for bank, base_url in input_data:
        pdf_urls = scraper.scrape_pdf_urls(base_url)

        for pdf_url in pdf_urls:
            resolved_pdf_url = resolve_pdf_url(base_url, pdf_url)
            output_data.append((bank, base_url, pdf_url, resolved_pdf_url))

    logger.info(f"Total number of unique PDF URLs found: {len(output_data)}")
    write_output_csv(output_file_path, output_data)


if __name__ == '__main__':
    scrape_to_file(
        input_file_path='./src/scrape/input_urls_1000.csv',
        webdriver_path='./src/scrape/chromedriver',
        output_file_path='./src/scrape/pdf_urls_1000.csv'
    )