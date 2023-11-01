from src.config.logging import logger
import pandas as pd
import os 


def compute_precision(group: pd.DataFrame) -> float:
    """Compute precision for a given query group."""
    return group['HUMAN_LABEL'].mean()

def compute_p_at_k(group: pd.DataFrame, k: int) -> float:
    """Compute precision at k for a given query group."""
    return group.head(k)['HUMAN_LABEL'].mean()

def compute_mrr(group: pd.DataFrame) -> float:
    """Compute mean reciprocal rank for a given query group."""
    rr = 1 / (group['HUMAN_LABEL'].to_numpy().nonzero()[0][0] + 1) if group['HUMAN_LABEL'].to_numpy().nonzero()[0].size != 0 else 0
    return rr

def _compute_dcg(group: pd.DataFrame) -> float:
    """Compute discounted cumulative gain for a given query group."""
    rel_vector = group['HUMAN_LABEL'].values
    return sum([rel / (i + 2) for i, rel in enumerate(rel_vector)])

def compute_ndcg(group: pd.DataFrame) -> float:
    """Compute normalized discounted cumulative gain for a given query group."""
    dcg = _compute_dcg(group)
    idcg = sum([1 / (i + 2) for i in range(len(group))])
    return dcg / idcg if idcg > 0 else 0

def _compute_dcg_at_k(group: pd.DataFrame, k: int) -> float:
    """Compute discounted cumulative gain at k for a given query group."""
    rel_vector = group['HUMAN_LABEL'].head(k).values
    return sum([rel / (i + 2) for i, rel in enumerate(rel_vector)])

def compute_ndcg_at_k(group: pd.DataFrame, k: int) -> float:
    """Compute normalized discounted cumulative gain at k for a given query group."""
    dcg = _compute_dcg_at_k(group, k)
    idcg = sum([1 / (i + 2) for i in range(min(len(group), k))])
    return dcg / idcg if idcg > 0 else 0

def compute_all_metrics(file_path: str) -> pd.DataFrame:
    """
    Computes precision metrics including MRR, NDCG and their variants at specific positions 
    for search results data.
    """
    logger.info("Loading data from %s", file_path)
    data = pd.read_excel(file_path)

    logger.info("Filtering data...")
    filtered_data = data.groupby('query').filter(lambda group: group['HUMAN_LABEL'].sum() > 0)

    # Metrics containers
    metrics = {
        'query': [],
        'p': [],
        'p@1': [],
        'p@3': [],
        'p@5': [],
        'mrr': [],
        'ndcg': [],
        'ndcg@3': [],
        'ndcg@5': []
    }

    # Compute metrics for each query
    for query, group in filtered_data.groupby('query'):
        metrics['query'].append(query)
        metrics['p'].append(compute_precision(group))
        metrics['p@1'].append(compute_p_at_k(group, 1))
        metrics['p@3'].append(compute_p_at_k(group, 3))
        metrics['p@5'].append(compute_p_at_k(group, 5))
        metrics['mrr'].append(compute_mrr(group))
        metrics['ndcg'].append(compute_ndcg(group))
        metrics['ndcg@3'].append(compute_ndcg_at_k(group, 3))
        metrics['ndcg@5'].append(compute_ndcg_at_k(group, 5))

    # Convert metrics to DataFrame
    result_df = pd.DataFrame(metrics)

    # Compute and append average metrics
    avg_row = {
        'query': 'Average',
        'p': result_df['p'].mean(),
        'p@1': result_df['p@1'].mean(),
        'p@3': result_df['p@3'].mean(),
        'p@5': result_df['p@5'].mean(),
        'mrr': result_df['mrr'].mean(),
        'ndcg': result_df['ndcg'].mean(),
        'ndcg@3': result_df['ndcg@3'].mean(),
        'ndcg@5': result_df['ndcg@5'].mean()
    }
    avg_df = pd.DataFrame([avg_row])
    result_df = pd.concat([result_df, avg_df], ignore_index=True)

    logger.info("Computation complete.")
    return result_df

def compute(input_path: str, output_path: str):
    """Main function to compute metrics and save to CSV."""
    result_df = compute_all_metrics(input_path)
    logger.info("Saving results to %s", output_path)
    result_df.to_csv(output_path, index=False)
    logger.info("Results saved successfully.")

if __name__ == "__main__":
    input_file_path = "./data/evaluate/site-search-results.xlsx"
    output_file_path = "./data/metrics/site-search.csv"
    output_directory = os.path.dirname(output_file_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    compute(input_file_path, output_file_path)