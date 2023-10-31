from src.utils.reports import jsonl_to_excel


if __name__ == '__main__':
    jsonl_to_excel('./data/evaluate/site-search-results.jsonl',  './data/evaluate/site-search-results.xlsx')
    jsonl_to_excel('./data/evaluate/site-search-results-pruned.jsonl',  './data/evaluate/site-search-results-pruned.xlsx')