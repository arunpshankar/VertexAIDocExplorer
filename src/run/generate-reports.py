from src.utils.reports import jsonl_to_excel_site_search
from src.utils.reports import jsonl_to_excel_doc_search


if __name__ == '__main__':
    jsonl_to_excel_site_search("./data/evaluate/site-search-results.jsonl", "./data/evaluate/site-search-results.xlsx")
    jsonl_to_excel_site_search("./data/evaluate/site-search-results-pruned.jsonl", "./data/evaluate/site-search-results-pruned.xlsx")
    jsonl_to_excel_doc_search("./data/evaluate/doc-search-results.jsonl", "./data/evaluate/doc-search-results.xlsx")