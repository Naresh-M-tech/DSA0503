"""
Data Profiler Module
Generates data quality profiles and examination reports.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List


def profile_dataset(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """Generate a comprehensive profile of a dataset.

    Args:
        df: The DataFrame to profile
        dataset_name: Name of the dataset for reporting

    Returns:
        Dictionary containing profile information
    """
    if df is None or df.empty:
        return {"error": "Dataset is empty or None"}

    profile = {
        "name": dataset_name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {},
        "missing_percentages": {},
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_values": {},
        "statistics": {},
    }

    for col in df.columns:
        # Missing values
        missing = int(df[col].isnull().sum())
        profile["missing_values"][col] = missing
        profile["missing_percentages"][col] = round((missing / len(df)) * 100, 2)

        # Unique values
        profile["unique_values"][col] = int(df[col].nunique())

        # Statistics
        if pd.api.types.is_numeric_dtype(df[col]):
            col_data = pd.to_numeric(df[col], errors="coerce")
            profile["statistics"][col] = {
                "mean": round(float(col_data.mean()), 2) if not col_data.isnull().all() else None,
                "median": round(float(col_data.median()), 2) if not col_data.isnull().all() else None,
                "std": round(float(col_data.std()), 2) if not col_data.isnull().all() else None,
                "min": float(col_data.min()) if not col_data.isnull().all() else None,
                "max": float(col_data.max()) if not col_data.isnull().all() else None,
                "25%": float(col_data.quantile(0.25)) if not col_data.isnull().all() else None,
                "50%": float(col_data.quantile(0.50)) if not col_data.isnull().all() else None,
                "75%": float(col_data.quantile(0.75)) if not col_data.isnull().all() else None,
            }
        else:
            top_values = df[col].value_counts().head(5).to_dict()
            profile["statistics"][col] = {
                "top_values": {str(k): int(v) for k, v in top_values.items()},
                "most_frequent": str(df[col].mode().iloc[0]) if not df[col].mode().empty else None,
            }

    return profile


def create_quality_summary_table(profile: Dict[str, Any]) -> pd.DataFrame:
    """Create a readable quality summary table from a profile."""
    rows = []
    for col in profile.get("column_names", []):
        row = {
            "Column": col,
            "Data Type": profile.get("dtypes", {}).get(col, "Unknown"),
            "Missing Count": profile.get("missing_values", {}).get(col, 0),
            "Missing %": f"{profile.get('missing_percentages', {}).get(col, 0):.1f}%",
            "Unique Values": profile.get("unique_values", {}).get(col, 0),
        }
        rows.append(row)

    return pd.DataFrame(rows)


def get_statistical_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Get statistical summary using pandas describe()."""
    if df is None or df.empty:
        return pd.DataFrame()

    desc = df.describe(include="all").round(2)
    return desc


def get_basic_info(df: pd.DataFrame) -> pd.DataFrame:
    """Get basic info similar to df.info() but as a DataFrame."""
    if df is None or df.empty:
        return pd.DataFrame()

    info_rows = []
    for col in df.columns:
        info_rows.append({
            "Column": col,
            "Non-Null Count": int(df[col].count()),
            "Dtype": str(df[col].dtype),
            "Null Count": int(df[col].isnull().sum()),
            "Unique": int(df[col].nunique()),
        })

    return pd.DataFrame(info_rows)
