from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chat_models import ChatVertexAI
from src.config.logging import logger
import json


MODEL_NAME = 'chat-bison'

class LLM:
    def __init__(self):
        # Initialize topics list
        self.topics = []
        
        # Load the model
        self.model = self.load_model()
        
        # Load topics from the provided JSONL file
        self.load_jsonl('./config/topics.jsonl')

    def load_model(self):
        """Load the chat model from Vertex AI."""
        model = ChatVertexAI(model_name=MODEL_NAME, temperature=0, max_output_tokens=512, verbose=True)
        return model

    def load_jsonl(self, filepath):
        """Load the topics from the provided JSONL file."""
        with open(filepath, 'r') as file:
            for line in file:
                self.topics.append(json.loads(line))

    def construct_prompt(self, page_content, pdf_url):
        pass

    def classify(self, prompt):
        """
        Get the model's classification based on the prompt.
        
        Parameters:
        - prompt: Text prompt for classification
        
        Returns:
        - completion: Model's response
        """
        response = self.model(prompt)
        completion = response.content.strip()
        return completion


if __name__ == '__main__':
    llm = LLM()
    llm.classify('')