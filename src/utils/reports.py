from src.config.logging import logger
import pandas as pd
import openpyxl
import json

def wrap_text_fixed_size(text, line_length=50):
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

def jsonl_to_excel(input_path, output_path):
    """
    Convert a JSONL file to a formatted Excel file.

    Parameters:
    - input_path (str): Path to the input JSONL file.
    - output_path (str): Path to the output Excel file.
    """
    logger.info(f"Reading JSONL data from {input_path}...")
    
    data = []
    with open(input_path, "r") as file:
        for line in file:
            data.append(json.loads(line))
    df = pd.DataFrame(data)
    logger.info(f"Successfully loaded {len(df)} records from {input_path}.")

    logger.info("Wrapping text for improved readability in Excel...")
    df_wrapped = df.map(lambda x: wrap_text_fixed_size(str(x)) if pd.notnull(x) else x)

    logger.info("Converting 'rank' column to numeric...")
    df_wrapped['rank'] = pd.to_numeric(df_wrapped['rank'])

    logger.info(f"Saving data to Excel file {output_path}...")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_wrapped.to_excel(writer, sheet_name="Search Results", index=False)

    logger.info("Adjusting Excel formatting for improved readability...")
    wb = openpyxl.load_workbook(output_path)
    ws = wb.active

    for col in ws.columns:
        max_height = 15
        for cell in col:
            cell.alignment = openpyxl.styles.Alignment(wrap_text=True)
            if cell.value and isinstance(cell.value, str):
                lines = cell.value.count('\n') + 1
                height = 15 * lines
                max_height = max(max_height, height)
        for cell in col:
            ws.row_dimensions[cell.row].height = max_height

    wb.save(output_path)
    logger.info(f"Successfully saved formatted data to {output_path}.")