from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup
import logging
import time
from typing import List

def scrape_pdf_urls(url: str, webdriver_path: str) -> List[str]:
    """
    Scrape all PDF URLs from a given webpage.

    Args:
    url (str): The URL of the webpage to scrape.
    webdriver_path (str): The path to the Chrome WebDriver executable.

    Returns:
    List[str]: A list of found PDF URLs.
    """

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode

    # Initialize the WebDriver
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        logging.info("Opening the webpage.")
        driver.get(url)

        # Wait for JavaScript to load
        time.sleep(5)  # Adjust time as needed

        # Get the HTML content after JavaScript execution
        html_content = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <a> tags with href attribute
        a_tags = soup.find_all('a', href=True)

        # Filter out URLs that end with '.pdf'
        pdf_urls = [tag['href'] for tag in a_tags if tag['href'].endswith('.pdf')]

        # Close the WebDriver
        driver.quit()

        return pdf_urls

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        driver.quit()
        return []

if __name__ == "__main__":
    # URL of the webpage to scrape
    url = "https://www.brooklinebancorp.com/sec-filings/Docs/default.aspx"

    # Path to the WebDriver executable
    webdriver_path = './src/playground/chromedriver'

    pdf_urls = scrape_pdf_urls(url, webdriver_path)
    for pdf_url in pdf_urls:
        logging.info(f"Found PDF URL: {pdf_url}")