from src.evaluate.site_search import evaluate_site_search
from src.evaluate.doc_search import evaluate_doc_search
from src.evaluate.site_search import evaluate_pruner


if __name__ == '__main__':
    evaluate_site_search('./config/site-search-queries.jsonl', './data/evaluate/site-search-results.jsonl')
    evaluate_pruner('./data/evaluate/site-search-results.jsonl', './data/evaluate/site-search-results-pruned.jsonl')
    evaluate_doc_search('./config/doc-search-queries.jsonl', './data/evaluate/doc-search-results.jsonl')