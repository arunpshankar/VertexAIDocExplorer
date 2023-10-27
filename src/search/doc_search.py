from src.config.logging import logger
from src.config.setup import config
from typing import Dict, Any, List
import requests


def create_conversation() -> str:
    """
    Create a new conversation and return its ID.
    
    Returns:
        str: The ID of the newly created conversation.
    """
    url = f"https://discoveryengine.googleapis.com/v1/projects/{config.PROJECT_ID}/locations/global/collections/default_collection/dataStores/{config.DOC_SEARCH_DATA_STORE_ID}/conversations"

    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "user_pseudo_id": config.USER_PSEUDO_ID
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    conversation_id = response.json()['name'].split('/')[-1]
    logger.info(f"Created a new conversation with ID: {conversation_id}")

    return conversation_id


def chat(query: str, conversation_id: str) -> Dict[str, Any]:
    """
    Generate a conversational search response.

    Args:
        query (str): The user's query.
        conversation_id (str): The ID of the conversation.

    Returns:
        dict: The JSON response from the chat API.
    """
    url = f"https://discoveryengine.googleapis.com/v1/projects/{config.PROJECT_ID}/locations/global/collections/default_collection/dataStores/{config.DOC_SEARCH_DATA_STORE_ID}/conversations/{conversation_id}:converse"

    headers = {
        "Authorization": f"Bearer {config.ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": {"input": query}
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()


def display_search_results(search_results: List[Dict[str, Any]]) -> None:
    """
    Display the search results.

    Args:
        search_results (list): A list of search result dictionaries.
    """
    for result in search_results:
        logger.info('-' * 10)
        data = result['document']['derivedStructData']
        link = data['link']
        answers = data['extractive_answers']

        logger.info(f'Doc ==> {link}')
        for i, answer in enumerate(answers):
            page_number = answer['pageNumber']
            content = answer['content'].strip()
            logger.info(f'Segment ==> {content}')
            logger.info(f'Page ==> {page_number}')
            logger.info('=' * 100)


if __name__ == "__main__":
    query = "what is hsbc's lcr for the year 2021?"  # LCR ==> liquidity coverage ratio

    conversation_id = create_conversation()
    response = chat(query, conversation_id)

    summary_text = response['reply']['summary']['summaryText']
    logger.info(f"Summary Text: {summary_text}")

    conversation = response['conversation']
    logger.info(f"Conversation: {conversation}")

    search_results = response['searchResults']
    display_search_results(search_results)
