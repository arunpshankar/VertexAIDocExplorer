from typing import List, Dict, Optional, Any
from src.config.logging import logger
from tqdm import tqdm
import subprocess
import requests
import yaml
import json
import os


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config.yaml file.
    
    Returns:
        dict: The configuration data.
    """
    with open("config/config.yaml", 'r') as stream:
        config_data = yaml.safe_load(stream)
    return config_data

config = load_config()
PROJECT_ID = config['project_id']
DATA_STORE_ID = config['datastore_id']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['credentials_json']


def get_access_token() -> str:
    """
    Fetch an access token for authentication.
    
    Returns:
        str: The fetched access token.
    """
    logger.info("Fetching access token...")
    cmd = ["gcloud", "auth", "print-access-token"]
    token = subprocess.check_output(cmd).decode('utf-8').strip()
    logger.info("Access token obtained successfully.")
    return token


class DiscoveryResponse:
    def __init__(self, result: Dict[str, Any]):
        doc_data = result['document']['derivedStructData']
        self.title = doc_data['title']
        self.link = doc_data['link']
        self.snippet = doc_data['snippets'][0]['snippet']
        metatags = doc_data['pagemap']['metatags'][0]
        self.p_title = metatags['title']
        self.subject = metatags['subject']
        self.author = metatags['author']
        self.creationdate = metatags['creationdate']
        
    def log_details(self):
        logger.info(f'Title: {self.title}')

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "p_title": self.p_title,
            "subject": self.subject,
            "author": self.author,
            "creationdate": self.creationdate
        }



def search_discovery_engine(query: str, page_size: int = 10, page_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the Discovery Engine with a specified query.
    
    Args:
        query (str): The search query.
        page_size (int, optional): The number of results to fetch per page. Defaults to 10.
        page_token (str, optional): The token for pagination. Defaults to None.
        
    Returns:
        dict: The JSON response from the Discovery Engine.
    """
    logger.info(f"Searching Discovery Engine with query: `{query}`...")
    access_token = get_access_token()
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}/servingConfigs/default_search:search"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "servingConfig": f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{DATA_STORE_ID}/servingConfigs/default_search",
        "query": query,
        "pageSize": page_size
    }
    if page_token:
        payload["pageToken"] = page_token
    
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        logger.error(f"Failed to search. Status code: {response.status_code}. Response: {response.text}")
    else:
        logger.info(f"Search successful. Found {len(response.json().get('results', []))} results.")
    
    return response.json()


def fetch_all_results(query: str, page_size: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch all search results by paginating through the Discovery Engine.
    
    Args:
        query (str): The search query.
        page_size (int, optional): The number of results to fetch per page. Defaults to 10.
        
    Returns:
        list: A list of all fetched search results.
    """
    all_results = []
    next_page_token = None
    page_count = 1
    while True:
        logger.info(f"Fetching page {page_count}...")
        response = search_discovery_engine(query, page_size=page_size, page_token=next_page_token)
        all_results.extend(response['results'])
        
        # Check if there's a next page
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            logger.info("All pages fetched successfully.")
            break
        page_count += 1
    return all_results


def save_to_jsonl(results: List[Dict[str, Any]], filename: str) -> None:
    """
    Save the search results to a JSONL file.
    
    Args:
        results (list): A list of search results.
        filename (str): The name of the file to save the results to.
    """
    logger.info(f"Saving results to {filename}...")
    with open(filename, 'w') as f:
        for result in tqdm(results, desc="Saving results"):
            response = DiscoveryResponse(result)
            f.write(json.dumps(response.to_dict()) + '\n')
    logger.info(f"Saved {len(results)} results to {filename}.")


# Sample usage
query = 'filetype:pdf hsbc disclosure reports'
all_results = fetch_all_results(query)
save_to_jsonl(all_results, './data/results.jsonl')
