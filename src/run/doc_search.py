from src.search.doc_search import transform_search_results
from src.search.doc_search import create_conversation
from src.search.doc_search import save_to_jsonl
from src.search.doc_search import chat


def doc_search_test(query: str) -> None:
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
    doc_search_test(query='annual report "commerzbank"')