from src.prune.pruner import Pruner


if __name__ == '__main__':
    pruner = Pruner()
    pruner.prune(input_file_path='./data/site-search-results.jsonl', output_file_path='./data/site-search-results-pruned.jsonl')