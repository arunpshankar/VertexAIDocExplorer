from src.config.logging import logger
from openpyxl.styles import Alignment
from pandas import DataFrame
import pandas as pd
import openpyxl
import json


def _wrap_text_fixed_size(text: str, line_length: int = 50) -> str:
    """
    Wrap text into multiple lines of fixed size.

    Parameters:
    - text (str): The input text to be wrapped.
    - line_length (int): The desired line length for wrapping.

    Returns:
    - str: Wrapped text.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) > line_length:
            lines.append(' '.join(current_line))
            current_line = []
            current_length = 0
        current_line.append(word)
        current_length += len(word) + 1

    lines.append(' '.join(current_line))
    return '\n'.join(lines)


def _break_segments(segments: list) -> str:
    """
    Format segments into a readable string.

    Parameters:
    - segments (list): List of segment dictionaries.

    Returns:
    - str: Formatted string with segments.
    """
    bullets = [f"{i+1}) {segment['segment']} [Page: {segment['page']}]" for i, segment in enumerate(segments)]
    return '\n'.join(bullets)


def _reorder_columns(df: DataFrame) -> DataFrame:
    """
    Reorder DataFrame columns to have 'answer' after 'question'.

    Parameters:
    - df (DataFrame): The input DataFrame.

    Returns:
    - DataFrame: Reordered DataFrame.
    """
    columns_order = list(df.columns)
    answer_idx = columns_order.index('answer')
    question_idx = columns_order.index('question')
    columns_order.insert(question_idx + 1, columns_order.pop(answer_idx))
    return df[columns_order]


def _load_jsonl(input_path: str) -> list:
    """
    Load data from a JSONL file.

    Parameters:
    - input_path (str): Path to the input JSONL file.

    Returns:
    - list: List of dictionaries from JSONL data.
    """
    with open(input_path, "r") as file:
        return [json.loads(line) for line in file]


def _save_to_excel(df: DataFrame, output_path: str):
    """
    Save a DataFrame to an Excel file.

    Parameters:
    - df (DataFrame): Data to save.
    - output_path (str): Path to the output Excel file.
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Search Results", index=False)


def jsonl_to_excel_site_search(input_path: str, output_path: str, max_rank: int):
    """
    Convert a JSONL file to a formatted Excel file, including only rows with rank less than or equal to max_rank.

    Parameters:
    - input_path (str): Path to the input JSONL file.
    - output_path (str): Path to the output Excel file.
    - max_rank (int): Maximum rank to include in the output.
    """
    logger.info(f"Reading JSONL data from {input_path}...")
    data = _load_jsonl(input_path)
    df = pd.DataFrame(data)

    # Filter the DataFrame based on the rank
    df_filtered = df[df['new_rank'] <= max_rank]

    logger.info(f"Successfully loaded {len(df_filtered)} records from {input_path}.")

    df_filtered = df_filtered.map(lambda x: _wrap_text_fixed_size(str(x)) if pd.notnull(x) else x)
    df_filtered['rank'] = pd.to_numeric(df_filtered['rank'])
    df_filtered['new_rank'] = pd.to_numeric(df_filtered['new_rank'])
    df_filtered['link'] = df_filtered['link'].str.replace('\n', '')
    
    logger.info(f"Saving data to Excel file {output_path} with max rank {max_rank}...")
    _save_to_excel(df_filtered, output_path)

    # Adjust Excel formatting
    wb = openpyxl.load_workbook(output_path)
    ws = wb.active
    for col in ws.columns:
        max_height = 15
        for cell in col:
            cell.alignment = Alignment(wrap_text=True)
            if cell.value and isinstance(cell.value, str):
                lines = cell.value.count('\n') + 1
                max_height = max(max_height, 15 * lines)
        for cell in col:
            ws.row_dimensions[cell.row].height = max_height

    wb.save(output_path)
    logger.info(f"Successfully saved formatted data with max rank {max_rank} to {output_path}.")


def jsonl_to_excel_doc_search(input_path: str, output_path: str):
    """
    Convert a JSONL file to a formatted Excel file.

    Parameters:
    - input_path (str): Path to the input JSONL file.
    - output_path (str): Path to the output Excel file.
    """
    logger.info(f"Reading JSONL data from {input_path}...")
    data = _load_jsonl(input_path)
    df = pd.DataFrame(data)
    df = _reorder_columns(df)
    df['segments'] = df['segments'].apply(_break_segments)
    df['rank'] = pd.to_numeric(df['rank'])
    
    logger.info(f"Saving data to Excel file {output_path}...")
    _save_to_excel(df, output_path)

    # Adjust Excel formatting
    wb = openpyxl.load_workbook(output_path)
    ws = wb.active
    for col in ws.columns:
        max_length = max([len(str(cell.value)) for cell in col if cell.value])
        col_width = max_length / 5
        ws.column_dimensions[col[0].column_letter].width = col_width
        for cell in col:
            cell.alignment = Alignment(wrap_text=True)

    wb.save(output_path)
    logger.info(f"Successfully saved formatted data to {output_path}.")