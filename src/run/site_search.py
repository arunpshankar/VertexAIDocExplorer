from src.search.site_search import search_discovery_engine
from src.search.site_search import DiscoveryResponse
from src.search.site_search import fetch_all_results
from src.search.site_search import save_to_jsonl
from src.config.logging import logger 
from pprint import pprint


def site_search_test(query: str) -> None:
    """
    Search the site based on the given query and log the results.

    Args:
        query (str): Search query.

    Returns:
        None
    """
    try:
        response = search_discovery_engine(query=query)
        results = response.get('results', [])

        print(f'==================================================== SEARCH HITS ====================================================')
        for result in results:
            discovery_response = DiscoveryResponse(result)
            pprint(discovery_response.to_dict())
            print('-' * 120)
    except Exception as e:
        logger.error(f"Error while testing site search: {e}")

def site_search_paginate_test(query: str) -> None:
    try:
        results = fetch_all_results(query)

        print(f'==================================================== SEARCH HITS ====================================================')
        for result in results:
            discovery_response = DiscoveryResponse(result)
            pprint(discovery_response.to_dict())
            print('-' * 120)

        save_to_jsonl(results, './data/site-search-results.jsonl')
    except Exception as e:
        logger.error(f"Error while testing site search pagination: {e}")


if __name__ == "__main__":
    query = 'filetype:pdf hsbc disclosure reports'
    # site_search_test(query)

    query = 'filetype:pdf brooklinebancorp disclosure reports'
    site_search_paginate_test(query)
