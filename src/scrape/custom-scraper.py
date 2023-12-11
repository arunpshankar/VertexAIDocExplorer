from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from src.config.logging import logger
from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List, Set
import time


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
            time.sleep(5)  # Wait for JavaScript to load
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
        urls = self._scrape_urls_from_page(base_url)
        for url in urls:
            if ".pdf" in url and 'inline' in url:
                pdf_url = base_url + url.split('?')[0]
                unique_pdf_urls.add(pdf_url)

        return unique_pdf_urls

def scrape_to_file(base_url: str, webdriver_path: str, output_file_path: str):
    """
    Scrape PDF URLs from a base URL and save them to a file.

    Args:
    base_url (str): The base URL to start scraping from.
    webdriver_path (str): The path to the Chrome WebDriver.
    output_file_path (str): The path to save the output file.
    """
    scraper = PDFScraper(webdriver_path)
    pdf_urls = scraper.scrape_pdf_urls(base_url)
    
    unique_non_pdf_urls = set()
    for url in scraper._scrape_urls_from_page(base_url):
        if ".pdf" not in url and "investor-relations" in url:
            unique_non_pdf_urls.add(url)

    for non_pdf_url in unique_non_pdf_urls:
        pdf_urls.update(scraper.scrape_pdf_urls(non_pdf_url))

    logger.info(f"Total number of unique PDF URLs found: {len(pdf_urls)}")
    with open(output_file_path, 'w+') as out:
        for url in pdf_urls:
            out.write(url + '\n')

if __name__ == '__main__':
    scrape_to_file(
        base_url="https://investor-relations.commerzbank.com/financial-reports",
        webdriver_path='./src/scrape/chromedriver',
        output_file_path='./src/scrape/pdf_urls.txt')
       