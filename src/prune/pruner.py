from src.config.logging import logger
from src.prune.llm import LLM
import json
import json


class Pruner:
    def __init__(self):
        self.llm = LLM()

    def is_pdf_url(self, url):
        """
        Check if the URL points to a PDF.
        """
        return url.lower().endswith('.pdf')

    def classify_content(self, content, child_url, llm_instance):
        """
        Classify the content into one of the specified topics using the LLM prompt.
        """
        prompt = llm_instance.construct_prompt(content, child_url)
        response_str = llm_instance.classify(prompt)
        clean_response_str = response_str.replace('```JSON\n', '').replace('```', '').strip()
        
        # Check the content before parsing
        if not clean_response_str:
            print(f"No content returned from LLM for URL: {child_url}")
            return 'Unclassified', 'No content to classify'

        try:
            classification_json = json.loads(clean_response_str)
            classification = classification_json['classification']
            rationale = classification_json['rationale']
            return classification, rationale
        except json.JSONDecodeError:
            print(f"Error decoding JSON for URL: {child_url}. Content: {clean_response_str}")
            return 'Unclassified', 'Error decoding response'
        

    def prune(self):
        pass

if __name__ == '__main__':
    pass