from src.search.site_search import search_discovery_engine
from src.search.site_search import DiscoveryResponse
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
        logger.error(f"Error while searching site: {e}")


if __name__ == "__main__":
    query = 'filetype:pdf hsbc disclosure reports'
    site_search_test(query)
