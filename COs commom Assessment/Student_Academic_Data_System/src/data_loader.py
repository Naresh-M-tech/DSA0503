"""
Data Loading Module
Handles loading of CSV, JSON, and XML files into Pandas DataFrames.
"""
import os
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Optional, Tuple, Dict


def load_csv(filepath: str) -> Tuple[Optional[pd.DataFrame], str]:
    """Load a CSV file into a DataFrame.

    Returns:
        Tuple of (DataFrame or None, error message or success message)
    """
    try:
        if not os.path.exists(filepath):
            return None, f"File not found: {filepath}"

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return None, f"File is empty: {filepath}"

        df = pd.read_csv(filepath, encoding="utf-8")
        if df.empty:
            return None, "The CSV file contains no data rows."

        return df, f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns."

    except pd.errors.EmptyDataError:
        return None, "The CSV file is empty or contains no parseable data."
    except pd.errors.ParserError as e:
        return None, f"CSV parsing error: {str(e)}"
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(filepath, encoding="latin-1")
            return df, f"Successfully loaded CSV (latin-1 encoding) with {len(df)} rows."
        except Exception as e:
            return None, f"Encoding error: {str(e)}"
    except Exception as e:
        return None, f"Error loading CSV: {str(e)}"


def load_json(filepath: str) -> Tuple[Optional[pd.DataFrame], str]:
    """Load a JSON file into a DataFrame.

    Returns:
        Tuple of (DataFrame or None, error message or success message)
    """
    try:
        if not os.path.exists(filepath):
            return None, f"File not found: {filepath}"

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return None, f"File is empty: {filepath}"

        with open(filepath, "r", encoding="utf-8") as f:
            data = pd.read_json(f, encoding="utf-8")

        if data.empty:
            return None, "The JSON file contains no data records."

        return data, f"Successfully loaded JSON with {len(data)} rows and {len(data.columns)} columns."

    except ValueError as e:
        return None, f"JSON parsing error: {str(e)}"
    except Exception as e:
        return None, f"Error loading JSON: {str(e)}"


def load_xml(filepath: str) -> Tuple[Optional[pd.DataFrame], str]:
    """Load an XML file into a DataFrame.

    Expects structure:
        <records>
            <record>
                <field_name>value</field_name>
                ...
            </record>
        </records>

    Returns:
        Tuple of (DataFrame or None, error message or success message)
    """
    try:
        if not os.path.exists(filepath):
            return None, f"File not found: {filepath}"

        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return None, f"File is empty: {filepath}"

        tree = ET.parse(filepath)
        root = tree.getroot()

        records = []
        for record_elem in root.findall("record"):
            record = {}
            for child in record_elem:
                record[child.tag] = child.text
            if record:
                records.append(record)

        if not records:
            return None, "No records found in the XML file."

        df = pd.DataFrame(records)
        return df, f"Successfully loaded XML with {len(df)} rows and {len(df.columns)} columns."

    except ET.ParseError as e:
        return None, f"XML parsing error: {str(e)}"
    except Exception as e:
        return None, f"Error loading XML: {str(e)}"


def detect_and_load(filepath: str) -> Tuple[Optional[pd.DataFrame], str, str]:
    """Detect file type by extension and load accordingly.

    Returns:
        Tuple of (DataFrame or None, file type string, message)
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    if ext == ".csv":
        df, msg = load_csv(filepath)
        return df, "CSV", msg
    elif ext == ".json":
        df, msg = load_json(filepath)
        return df, "JSON", msg
    elif ext in (".xml", ".htm", ".html"):
        df, msg = load_xml(filepath)
        return df, "XML", msg
    else:
        return None, "Unknown", f"Unsupported file format: {ext}. Supported formats: .csv, .json, .xml"


def get_file_info(df: pd.DataFrame) -> Dict:
    """Get basic information about a loaded DataFrame."""
    info = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB",
    }
    return info
