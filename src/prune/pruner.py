from src.config.logging import logger
from src.prune.llm import LLM
import jsonlines
import json 

class Pruner:
    """
    A utility class responsible for pruning site search results.
    
    This class reads from a provided JSONL file containing site search results, classifies the results based on the 
    content of the 'link' field, and writes back the updated results to a new JSONL file.
    """
    def __init__(self) -> None:
        """Initializes the Pruner with an instance of LLM for classification."""
        self.llm = LLM()
        logger.info("Pruner initialized.")

    def _parse_llm_response(self, response: str) -> dict:
        """
        Parse the response from LLM.
        
        Args:
            response (str): The raw response from LLM.
        
        Returns:
            dict: The parsed response as a dictionary.
        """
        cleaned_response = response.replace('```JSON\n', '').replace('```', '').strip()
        return json.loads(cleaned_response)

    def prune(self, site_search_results_file_path: str) -> None:
        """
        Read the provided file, classify its content, and write back the updated content.

        Args:
            site_search_results_file_path (str): Path to the file containing site search results.
        """
        output_file_path = './data/site-search-results-pruned.jsonl'
        
        try:
            logger.info(f"Starting processing of file: {site_search_results_file_path}")
            
            with jsonlines.open(site_search_results_file_path, mode='r') as reader, \
                 jsonlines.open(output_file_path, mode='w') as writer:
                
                for entry in reader:
                    link = entry.get('link')
                    logger.info(f"Processing entry with link: {link}")
                    
                    response = self.llm.classify(entry)
                    parsed_response = self._parse_llm_response(response)
                    
                    logger.info(f"Classification result: {parsed_response.get('classification', 'N/A')}")
                    
                    # Check if the 'classification' key exists and isn't 'unclassified'
                    if parsed_response.get('classification', '').lower() != 'unclassified':
                        entry.update(parsed_response)
                        writer.write(entry)
                        logger.info(f"Entry with link {link} written to output file.")
            
            logger.info(f"Finished processing of file: {site_search_results_file_path}")
            
        except Exception as e:
            logger.error(f"Error processing file {site_search_results_file_path}. Entry: {entry}. Error: {e}")

if __name__ == '__main__':
    pruner = Pruner()
    pruner.prune('./data/site-search-results.jsonl')
