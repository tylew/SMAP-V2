import pandas as pd
from pathlib import Path
import io

def df_from_file(filepath, **params) -> pd.DataFrame:
    """
    Extract df from .CSV or .XLSX file

    Parameters:
    filepath: The path to the file to be extracted
    params: Additional parameters to pass to pd.read_excel or pd.read_csv
    """
    try:
        file_extension = filepath.name.split('.')[-1]
    except:
        file_extension = filepath.split('.')[-1]
    try:
        if file_extension in ["xlsx", "xls"]:
            return pd.read_excel(filepath, **params)   
        elif file_extension == "csv":
            return pd.read_csv(filepath, **params)
    # except ValueError:
    #     raise ValueError(f"Unrecognized file extension: {file_extension}")
    except Exception as e: 
        txt = f"Error reading file on re-run most likely. Need to debug. {e}"
        print(txt)
        raise Exception('Error reading file, please re-upload')

def make_excel_workbook(df_list, sheet_name_list):
    """
    Create an Excel file from a list of DataFrames and corresponding sheet names.

    Parameters
    ----------
    df_list : list of pd.DataFrame
        List of DataFrames to be written to the Excel file.
    sheet_name_list : list of str
        List of sheet names corresponding to each DataFrame.

    Returns
    -------
    bytes
        A bytes object containing the Excel file data.
    """
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for df, sheet_name in zip(df_list, sheet_name_list):
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    buffer.seek(0)
    return buffer.getvalue()


def reverseDF(df):
    """reverses a dataframe"""
    df = df[::-1]
    return df