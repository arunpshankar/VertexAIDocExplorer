from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain.prompts.chat import HumanMessagePromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chat_models import ChatVertexAI
from src.config.logging import logger
from src.config.setup import config
from typing import List, Dict
import jsonlines


MODEL_NAME = 'chat-bison'

class LLM:
    """Language Learning Model for classifying finance-related PDFs based on topics."""
    
    def __init__(self, topics_filepath: str = './config/topics.jsonl'):
        """Initialize the LLM instance by loading topics and model."""
        self.topics = self._load_topics_from_jsonl(topics_filepath)
        self.model = self._initialize_model()

    def _initialize_model(self) -> ChatVertexAI:
        """Load the chat model from Vertex AI."""
        try:
            return ChatVertexAI(model_name=MODEL_NAME, temperature=0, max_output_tokens=512, verbose=True)
        except Exception as e:
            logger.error(f"Failed to load the model: {e}")

    
    def _load_topics_from_jsonl(self, filepath: str) -> List[str]:
        """Load topics from the provided JSONL file."""
        topics = []
        try:
            with jsonlines.open(filepath) as reader:
                for topic in reader:
                    topics.append(topic)
        except Exception as e:
            logger.error(f"Failed to load topics from {filepath}: {e}")
        return topics
    
    def _get_topics_text(self) -> str:
        """
        Convert the topics into a formatted text representation.
        
        Returns:
            str: Formatted text representation of the topics.
        """
        topics_details = []
        for topic in self.topics:
            topic_info = (f"Topic: {topic['type']}\n"
                        f"Definition: {topic['definition']}\n"
                        f"Synonyms: {topic['synonyms']}\n")
            topics_details.append(topic_info)
            
        return '\n'.join(topics_details)


    @staticmethod
    def _convert_to_text_template(data: Dict[str, any]) -> str:
        """Convert a dictionary into a text template format with key in uppercase followed by value."""
        return '\n'.join([f"{key.upper()}: {value}" for key, value in data.items() if value is not None])

    def _construct_prompt(self, metadata: dict) -> str:
        """Construct a prompt based on the metadata."""
        pdf_url = metadata.pop('link', None)
        metadata_text = self._convert_to_text_template(metadata)
        topics_text = self._get_topics_text()
        
        system_template = f"""You are a finance research analyst. Your task is to classify the provided PDF URL and its metadata based on the list of topics below. 
If the PDF url or its metadata contains any terms related to the topics, classify accordingly. If you cannot classify, label it as 'unclassified'.

== TOPICS ==
{topics_text}"""
        system_message_prompt = SystemMessagePromptTemplate.from_template(template=system_template)
        human_template = f"""== PDF URL ==
{pdf_url}

== METADATA ==
{metadata_text}

Provide your classification along with the rationale behind your decision. 
Highlight any specific elements from the PDF URL or metadata that influenced your choice. 
If unclassified, explain why. 
Your response should be in a structured JSON format with two fields: `classification` and `rationale`.
NOTE: Focus on the SNIPPET under METADATA."""
        human_message_prompt = HumanMessagePromptTemplate.from_template(template=human_template)  
        chat_prompt = ChatPromptTemplate(messages=[system_message_prompt, human_message_prompt])
        prompt = chat_prompt.format_messages()
        return prompt

    def classify(self, metadata: dict) -> str:
        """Get the model's classification based on the provided metadata."""
        prompt = self._construct_prompt(metadata)
        try:
            response = self.model(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Failed to classify: {e}")