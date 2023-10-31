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
    # Load the JSONL data into a DataFrame
    data = []
    with open(input_path, "r") as file:
        for line in file:
            data.append(json.loads(line))
    df = pd.DataFrame(data)

    # Apply the text wrapping function to each cell in the DataFrame
    df_wrapped = df.applymap(lambda x: wrap_text_fixed_size(str(x)) if pd.notnull(x) else x)

    # Convert the 'rank' column to numeric
    df_wrapped['rank'] = pd.to_numeric(df_wrapped['rank'])

    # Save the modified DataFrame to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_wrapped.to_excel(writer, sheet_name="Search Results", index=False)

    # Adjust the Excel formatting
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

    # Save the final Excel file
    wb.save(output_path)


if __name__ == '__main__':
    jsonl_to_excel('./data/evaluate/site-search-results.jsonl',  './data/evaluate/site-search-results.xlsx')
