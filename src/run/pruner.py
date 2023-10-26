from src.prune.pruner import Pruner


if __name__ == '__main__':
    pruner = Pruner()
    pruner.prune('./data/site-search-results.jsonl')