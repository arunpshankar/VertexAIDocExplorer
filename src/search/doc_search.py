from src.config.logging import logger
from src.config.setup import config
from typing import List
from typing import Dict
from typing import Any
import jsonlines
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


def transform_search_results(question: str, search_results: List[Dict[str, Any]], answer: str) -> List[Dict[str, Any]]:
    """
    Transform the search results into the desired JSON structure with segments collapsed into a list
    and the summary text added as an "answer" field.

    Args:
        question (str): The incoming user question (query).
        search_results (list): A list of search result dictionaries.
        answer (str): The summary text to add as an "answer" field.

    Returns:
        List[Dict[str, Any]]: A list of transformed search results.
    """
    transformed_results = []
    for rank, result in enumerate(search_results):
        data = result['document']['derivedStructData']
        link = data['link']
        answers = data['extractive_answers']
        
        segments = [{"segment": answer['content'].strip(), "page": answer['pageNumber']} for answer in answers]
        
        transformed_result = {
            "question": question,
            "rank": rank + 1,
            "document": link,
            "segments": segments,
            "answer": answer
        }
        transformed_results.append(transformed_result)
    return transformed_results

def save_to_jsonl(data: List[Dict[str, Any]], filename: str = "results.jsonl") -> None:
    """
    Save the provided data to a .jsonl file.

    Args:
        data (List[Dict[str, Any]]): The data to save.
        filename (str, optional): The name of the file to save to. Defaults to "results.jsonl".
    """
    with jsonlines.open(filename, mode='w') as writer:
        for item in data:
            writer.write(item)

def get_and_save_results(query: str) -> None:
    """
    Process a user query to get search results, transform them into the updated JSON structure, display them, 
    and save them to a .jsonl file.

    Args:
        query (str): The user's query.
    """
    conversation_id = create_conversation()
    response = chat(query, conversation_id)

    summary_text = response['reply']['summary']['summaryText']
    
    search_results = response['searchResults']
    transformed_results = transform_search_results(query, search_results, summary_text)
    
    # Displaying the results
    for result in transformed_results:
        print(f"Rank = {result['rank']} | Document = {result['document']} | Answer = {result['answer']}")
        for segment in result['segments']:
            print(f"Segment = {segment['segment']} | Page = {segment['page']}")
        print('=' * 120)

    # Saving the results to a .jsonl file
    save_to_jsonl(transformed_results)


if __name__ == '__main__':
    get_and_save_results(query='what is hsbc LCR 2021')