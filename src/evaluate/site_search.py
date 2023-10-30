from src.search.site_search import DiscoveryResponse
from src.search.site_search import fetch_all_results
from src.config.logging import logger 
from src.prune.pruner import Pruner
import jsonlines


def evaluate_site_search(inp_file_path: str, out_file_path: str) -> None:
    """
    Evaluate the site search for each query in the input file and save the results in the output file.

    Args:
        inp_file_path (str): Path to the input JSONL file containing the evaluation queries.
        out_file_path (str): Path to the output JSONL file to save the evaluation site search results.
    """
    with jsonlines.open(inp_file_path, 'r') as reader, jsonlines.open(out_file_path, 'w') as writer:
        for data in reader:
            query = data.get('query')
            
            if not query:
                logger.warning(f"Missing query in data: {data}")
                continue

            results = fetch_all_results(query)

            for i, result in enumerate(results):
                rank = i + 1
                discovery_response = DiscoveryResponse(query, result, rank)
                
                logger.info(discovery_response.to_dict())
                
                writer.write(discovery_response.to_dict())
                
            logger.info('-' * 100)


def evaluate_pruner(inp_file_path: str, out_file_path: str) -> None:
    """
    Evaluate and prune results based on certain criteria.

    Args:
        inp_file_path (str): Path to the input JSONL file containing the site search results.
        out_file_path (str): Path to the output JSONL file to save the pruned results.
    """
    pruner = Pruner()
    pruner.prune(inp_file_path, out_file_path)


if __name__ == '__main__':
    evaluate_site_search('./config/site-search-queries.jsonl', './data/evaluate/site-search-results.jsonl')
    evaluate_pruner('./data/evaluate/site-search-results.jsonl', './data/evaluate/site-search-results-pruned.jsonl')