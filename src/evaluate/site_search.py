from src.search.site_search import search_discovery_engine
from src.search.site_search import DiscoveryResponse
from src.search.site_search import fetch_all_results
from src.search.site_search import save_to_jsonl
from src.config.logging import logger 
from pprint import pprint
import jsonlines


def site_search(query: str) -> dict:
    try:
        results = fetch_all_results(query)

        print(f'==================================================== SEARCH HITS ====================================================')
        for result in results:
            discovery_response = DiscoveryResponse(result)
            pprint(discovery_response.to_dict())
            print('-' * 120)
        
        #save_to_jsonl(results, './data/site-search-results.jsonl')
    except Exception as e:
        logger.error(f"Error while testing site search pagination: {e}")






def evaluate(inp_file: str, out_file: str = './output_results.jsonl') -> None:
    """
    Evaluate the site search for each query in the input file and save the results in the output file.

    Args:
        inp_file (str): Path to the input JSONL file containing the queries.
        out_file (str): Path to the output JSONL file to save the results.

    Returns:
        None
    """
    with jsonlines.open(inp_file, 'r') as reader, jsonlines.open(out_file, 'w') as writer:
        for data in reader:
            query = data.get('query')
            if query:
                results = site_search(query)
                writer.write(results)

if __name__ == '__main__':
    inp_file_path = './config/site-search-queries.jsonl'
    out_file_path = './data/evaluate/site-search-results.jsonl'
    evaluate(inp_file_path, out_file_path)
