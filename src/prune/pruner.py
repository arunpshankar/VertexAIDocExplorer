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

    def prune(self, input_file_path: str, output_file_path: str) -> None:
        """
        Read the provided file, classify its content, and write back the updated content.

        Args:
            site_search_results_file_path (str): Path to the file containing site search results.
        """
        
        logger.info(f"Starting processing of file: {input_file_path}")
        
        with jsonlines.open(input_file_path, mode='r') as reader, \
                jsonlines.open(output_file_path, mode='w') as writer:
            
            for entry in reader:
                try:
                    link = entry.get('link')
                    logger.info(f"Processing entry with link: {link}")
                    
                    response = self.llm.classify(entry)
                    parsed_response = self._parse_llm_response(response)
                    logger.info(f'Response = {parsed_response}')
                    
                    logger.info(f"Classification result: {parsed_response.get('classification', 'N/A')}")
                    
                    # Check if the 'classification' key exists and isn't 'unclassified'
                    if parsed_response.get('classification', '').lower() != 'unclassified':
                        # Update the entry with the parsed response
                        for key, value in parsed_response.items():
                            entry[key] = value
                        # Ensure the 'link' from the original entry is retained
                        entry['link'] = link

                        # Write the updated entry to the output file
                        writer.write(entry)
                        logger.info(f"Entry with link {link} written to output file.")
                except Exception as e:
                    logger.error(f"Error processing Entry: {entry}. Error: {e}")
        
        logger.info(f"Finished processing of file: {input_file_path}")