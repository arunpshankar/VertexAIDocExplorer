import json
import jsonlines
from src.config.logging import logger
from src.prune.llm import LLM

class Pruner:
    def __init__(self) -> None:
        self.llm = LLM()

    def _is_pdf_url(self, url: str) -> bool:
        """
        Check if the URL points to a PDF.
        
        Args:
        - url (str): The URL to check.
        
        Returns:
        - bool: True if the URL points to a PDF, otherwise False.
        """
        return url.lower().endswith('.pdf')

    def _parse_llm_response(self, response: str) -> dict:
        """
        Parse the response from LLM.
        
        Args:
        - response (str): The raw response from LLM.
        
        Returns:
        - dict: The parsed response as a dictionary.
        """
        cleaned_response = response.replace('```JSON\n', '').replace('```', '').strip()
        return json.loads(cleaned_response)

    def prune(self, site_search_results_file_path: str) -> None:
        """
        Read the provided file, classify its content, and write back the updated content.

        Args:
        - site_search_results_file_path (str): Path to the file containing site search results.
        """
        output_file_path = './data/site-search-results-pruned.jsonl'
        
        try:
            with jsonlines.open(site_search_results_file_path, mode='r') as reader, \
                 jsonlines.open(output_file_path, mode='w') as writer:
                
                for line in reader:
                    # Check for PDF URL in the 'link' field
                    link = line.get('link') 
                    if link and self._is_pdf_url(link):
                        # If it's a PDF link, classify it
                        response = self.llm.classify(line)
                        parsed_response = self._parse_llm_response(response)
                        
                        # Update the line with the response and write to a new file
                        line.update(parsed_response)

                    writer.write(line)

        except Exception as e:
            logger.error(f"Error processing file {site_search_results_file_path}: {e}")

if __name__ == '__main__':
    pruner = Pruner()
    print(pruner._is_pdf_url('http://dsfsdf.com/x.pdf'))
    pruner.prune('./data/site-search-results.jsonl')