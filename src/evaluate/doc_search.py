from src.search.doc_search import transform_search_results
from src.search.doc_search import create_conversation
from src.search.doc_search import chat
import jsonlines 
import time


def evaluate_doc_search(inp_file_path: str, out_file_path: str) -> None:
    """
    Evaluates the document search based on the given questions in the input file.
    Writes the results to the output file.

    Parameters:
    - inp_file_path (str): Path to the input file containing questions for document search.
    - out_file_path (str): Path to the output file where search results will be written.

    Returns:
    - None
    """

    with jsonlines.open(inp_file_path, 'r') as reader, jsonlines.open(out_file_path, 'w') as writer:
        for data in reader:
            question = data.get('question')
            if not question:
                continue

            print(f"Question: {question}")

            conversation_id = create_conversation()
            response = chat(question, conversation_id)

            summary_text = response['reply']['summary']['summaryText']
            search_results = response['searchResults']
            transformed_results = transform_search_results(question, search_results, summary_text)
            
            # Displaying the results and writing to the output file
            for result in transformed_results:
                print(f"Rank = {result['rank']} | Document = {result['document']} | Answer = {result['answer']}")
                segments_data = []
                for segment in result['segments']:
                    print(f"Segment = {segment['segment']} | Page = {segment['page']}")
                    segments_data.append({"segment": segment['segment'], "page": segment['page']})
                writer.write({
                    "question": question,
                    "rank": result['rank'],
                    "document": result['document'],
                    "segments": segments_data,
                    "answer": result['answer']
                })
                print('=' * 120)
            time.sleep(5)  # to avoid API throttling