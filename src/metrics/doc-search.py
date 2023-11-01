from src.config.logging import logger
from typing import List, Tuple
import pandas as pd
import numpy as np


def load_data(filepath: str) -> pd.DataFrame:
    """Load data from the provided Excel file."""
    return pd.read_excel(filepath)


def filter_and_parse_labels(data: pd.DataFrame) -> pd.DataFrame:
    """Filter out rows with "IGNORE" in the HUMAN_LABEL column and parse the labels."""
    data = data[data['HUMAN_LABEL'] != 'IGNORE'].copy()
    data['parsed_labels'] = data['HUMAN_LABEL'].str.split(',')
    return data


def compute_precision(labels: List[int]) -> float:
    """Compute the precision for a given set of labels."""
    return sum(labels) / len(labels) if labels else 0.0


def compute_precision_at_k(labels: List[int], k: int) -> float:
    """Compute the precision at position k."""
    return sum(labels[:k]) / k if k <= len(labels) else compute_precision(labels)


def compute_mrr(labels: List[int]) -> float:
    """Compute the Mean Reciprocal Rank (MRR) for a given set of labels."""
    for idx, label in enumerate(labels, 1):
        if label == 1:
            return 1 / idx
    return 0


def compute_dcg_at_k(labels: List[int], k: int) -> float:
    """Compute the Discounted Cumulative Gain (DCG) at position k."""
    return sum((2**label - 1) / np.log2(idx + 2) for idx, label in enumerate(labels[:k]))


def compute_ndcg(labels: List[int], k: int) -> float:
    """Compute the Normalized Discounted Cumulative Gain (nDCG) at position k."""
    dcg_k = compute_dcg_at_k(labels, k)
    idcg_k = compute_dcg_at_k(sorted(labels, reverse=True), k)
    return dcg_k / idcg_k if idcg_k else 0


def append_averages(data: pd.DataFrame) -> pd.DataFrame:
    """Append the average values for all metrics as the last row in the dataframe."""
    avg_data = {
        'question': 'AVERAGE',
        'MRR': data['MRR'].mean(),
        'nDCG': data['nDCG'].mean(),
        'nDCG@3': data['nDCG@3'].mean(),
        'nDCG@5': data['nDCG@5'].mean(),
        'precision': data['precision'].mean(),
        'p@1': data['p@1'].mean(),
        'p@3': data['p@3'].mean(),
        'p@5': data['p@5'].mean()
    }
    return pd.concat([data, pd.DataFrame([avg_data])], ignore_index=True)


def compute_all_metrics(labels: List[int]) -> Tuple[float, float, float, float]:
    """Compute all metrics (MRR, nDCG, nDCG@3, nDCG@5) for a given set of labels."""
    return (
        compute_mrr(labels),
        compute_ndcg(labels, len(labels)),
        compute_ndcg(labels, 3),
        compute_ndcg(labels, 5)
    )


def safe_convert_to_int(x: List[str]) -> List[int]:
    """Safely convert a list of strings to a list of integers."""
    return [int(label) for label in x] if isinstance(x, list) else []


def evaluate_by_metrics(input_filepath: str, output_filepath: str) -> None:
    """Generate metrics from an input Excel file and save the results to an output CSV file."""
    data = load_data(input_filepath)
    # Filter out rows with "not enough information" in the 'answer' column
    data = data[~data['answer'].str.contains('not enough information', case=False, na=False)]
    data = filter_and_parse_labels(data)
    data['parsed_labels'] = data['parsed_labels'].apply(safe_convert_to_int)

    consolidated_labels = data.groupby('question')['parsed_labels'].sum().reset_index()
    consolidated_labels['precision'] = consolidated_labels['parsed_labels'].apply(compute_precision)
    consolidated_labels['p@1'] = consolidated_labels['parsed_labels'].apply(lambda x: compute_precision_at_k(x, 1))
    consolidated_labels['p@3'] = consolidated_labels['parsed_labels'].apply(lambda x: compute_precision_at_k(x, 3))
    consolidated_labels['p@5'] = consolidated_labels['parsed_labels'].apply(lambda x: compute_precision_at_k(x, 5))

    consolidated_metrics = consolidated_labels['parsed_labels'].apply(compute_all_metrics)
    consolidated_labels['MRR'], consolidated_labels['nDCG'], consolidated_labels['nDCG@3'], consolidated_labels['nDCG@5'] = zip(*consolidated_metrics)

    consolidated_labels = append_averages(consolidated_labels)
    consolidated_labels[['question', 'precision', 'p@1', 'p@3', 'p@5', 'MRR', 'nDCG', 'nDCG@3', 'nDCG@5']].to_csv(output_filepath, index=False)
    
    logger.info(f"Metrics computed and saved to {output_filepath}")


if __name__ == '__main__':
    evaluate_by_metrics("data/evaluate/doc-search-results.xlsx", "data/metrics/doc-search-evaluation-by-metrics.csv")