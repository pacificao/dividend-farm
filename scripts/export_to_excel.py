import pandas as pd
from pathlib import Path

def export_dataframe_to_excel(df, output_dir="exports", filename="dividend_data.xlsx"):
    """
    Export the given DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): DataFrame to export.
        output_dir (str): Directory to save the Excel file in.
        filename (str): Name of the output Excel file.

    Returns:
        Path object to the exported file.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / filename

    try:
        df.to_excel(file_path, index=False)
        print(f"[+] Exported data to: {file_path}")
    except Exception as e:
        print(f"[!] Failed to export to Excel: {e}")
        return None

    return file_path