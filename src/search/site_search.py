from src.config.logging import logger
from src.config.setup import config
from typing import Optional
from typing import List
from typing import Dict
from typing import Any
from tqdm import tqdm
import requests
import json


class DiscoveryResponse:
    @staticmethod
    def _replace_braces_with_square_brackets(s):
        return s.replace('{', '[').replace('}', ']')

    def __init__(self, query: str, result: Dict[str, Any], rank: int):
        doc_data = result.get('document', {}).get('derivedStructData', {})
        
        self.query = query
        self.rank = rank
        self.title = doc_data.get('title', None)
        self.link = doc_data.get('link', None)
        snippets = doc_data.get('snippets', [])
        self.snippet = snippets[0]['snippet'] if snippets else None
        self.snippet = DiscoveryResponse._replace_braces_with_square_brackets(self.snippet)
        
        metatags = doc_data.get('pagemap', {}).get('metatags', [{}])[0]
        self.metatags_title = metatags.get('title', None)
        self.subject = metatags.get('subject', None)
        self.creationdate = metatags.get('creationdate', None)

    def to_dict(self) -> Dict[str, str]:
        return {
            "query": self.query,
            "rank": self.rank,
            "title": self.title,
            "link": self.link,
            "snippet": self.snippet,
            "metatags_title": self.metatags_title,
            "subject": self.subject,
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
    url = f"https://discoveryengine.googleapis.com/v1beta/projects/{config.PROJECT_ID}/locations/global/collections/default_collection/dataStores/{config.SITE_SEARCH_DATA_STORE_ID}/servingConfigs/default_search:search"
    
    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "servingConfig": f"projects/{config.PROJECT_ID}/locations/global/collections/default_collection/dataStores/{config.SITE_SEARCH_DATA_STORE_ID}/servingConfigs/default_search",
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
    all_results = []
    next_page_token = None
    page_count = 1

    while True:
        logger.info(f"Fetching page {page_count}...")

        response = search_discovery_engine(query, page_size=page_size, page_token=next_page_token)

        # Ensure 'results' key is present in the response
        results = response.get('results', [])
        if not results:
            logger.warning("No more results found.")
            break

        all_results.extend(results)

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