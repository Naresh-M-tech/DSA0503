"""
Outlier Detector Module
Detects statistical outliers (IQR) and domain-rule violations.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


# Domain validation rules: (min_valid, max_valid)
DOMAIN_RULES = {
    "Marks": (0, 100),
    "Attendance": (0, 100),
    "CGPA": (0, 10),
    "Credits": (0.5, 10),  # Positive non-zero
    "Semester": (1, 12),
    "Package_LPA": (0, 100),  # Non-negative, reasonable max
}


def detect_iqr_outliers(
    series: pd.Series,
    column_name: str = "Value",
) -> Dict:
    """Detect outliers using the IQR method.

    Args:
        series: Numeric pandas Series
        column_name: Name for reporting

    Returns:
        Dictionary with Q1, Q3, IQR, bounds, outlier count, and indices
    """
    numeric_data = pd.to_numeric(series, errors="coerce").dropna()

    if len(numeric_data) < 4:
        return {
            "column": column_name,
            "q1": None,
            "q3": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "outlier_count": 0,
            "outlier_indices": [],
        }

    q1 = float(numeric_data.quantile(0.25))
    q3 = float(numeric_data.quantile(0.75))
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (numeric_data < lower_bound) | (numeric_data > upper_bound)
    outlier_indices = numeric_data[outlier_mask].index.tolist()

    return {
        "column": column_name,
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "outlier_count": len(outlier_indices),
        "outlier_indices": outlier_indices,
    }


def detect_all_outliers(
    df: pd.DataFrame,
    columns: List[str] = None,
) -> Dict[str, Dict]:
    """Detect outliers in multiple columns of a DataFrame.

    Args:
        df: The DataFrame
        columns: List of column names to check (default: numeric columns)

    Returns:
        Dictionary mapping column names to their outlier info
    """
    if df is None or df.empty:
        return {}

    if columns is None:
        columns = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    results = {}
    for col in columns:
        if col in df.columns:
            results[col] = detect_iqr_outliers(df[col], col)

    return results


def validate_domain_rules(
    df: pd.DataFrame,
    student_id_col: str = "Student_ID",
) -> pd.DataFrame:
    """Validate domain rules and identify invalid vs extreme but valid values.

    Returns:
        DataFrame with columns: Student_ID, Attribute, Value, Outlier_Status, Treatment
    """
    if df is None or df.empty:
        return pd.DataFrame()

    records = []

    for attribute, (min_val, max_val) in DOMAIN_RULES.items():
        if attribute not in df.columns:
            continue

        for idx in df.index:
            value = df.at[idx, attribute]

            # Skip missing/NaN
            if pd.isna(value):
                continue

            try:
                num_val = float(value)
            except (ValueError, TypeError):
                # Non-numeric value in numeric field
                sid = df.at[idx, student_id_col] if student_id_col in df.columns else str(idx)
                records.append({
                    "Student_ID": sid,
                    "Attribute": attribute,
                    "Value": value,
                    "Outlier_Status": "Invalid (Non-numeric)",
                    "Treatment": "Flagged for review",
                })
                continue

            if num_val < min_val or num_val > max_val:
                sid = df.at[idx, student_id_col] if student_id_col in df.columns else str(idx)
                records.append({
                    "Student_ID": sid,
                    "Attribute": attribute,
                    "Value": num_val,
                    "Outlier_Status": "Invalid (Domain violation)",
                    "Treatment": "Convert to NaN",
                })

    return pd.DataFrame(records)


def detect_and_report_outliers(
    df: pd.DataFrame,
    student_id_col: str = "Student_ID",
) -> Tuple[pd.DataFrame, Dict[str, Dict]]:
    """Complete outlier detection: IQR statistical + domain rules.

    Returns:
        Tuple of (outlier report DataFrame, IQR results dictionary)
    """
    # IQR detection on key columns
    key_cols = [c for c in ["Marks", "Attendance", "Credits", "CGPA", "Package_LPA"]
                if c in df.columns]
    iqr_results = detect_all_outliers(df, key_cols)

    # Domain validation
    domain_report = validate_domain_rules(df, student_id_col)

    # Combine into a single report
    iqr_records = []
    for col_name, info in iqr_results.items():
        if info["outlier_count"] > 0:
            for idx in info["outlier_indices"]:
                val = df.at[idx, col_name]
                sid = df.at[idx, student_id_col] if student_id_col in df.columns else str(idx)

                # Check if it's also a domain violation
                if col_name in DOMAIN_RULES:
                    min_v, max_v = DOMAIN_RULES[col_name]
                    try:
                        nv = float(val)
                        is_invalid = nv < min_v or nv > max_v
                    except (ValueError, TypeError):
                        is_invalid = True
                else:
                    is_invalid = False

                iqr_records.append({
                    "Student_ID": sid,
                    "Attribute": col_name,
                    "Value": val,
                    "Outlier_Status": "Invalid (Domain violation)" if is_invalid else "Statistical outlier (IQR)",
                    "Treatment": "Convert to NaN" if is_invalid else "Flag for review (valid extreme)",
                })

    iqr_df = pd.DataFrame(iqr_records) if iqr_records else pd.DataFrame(
        columns=["Student_ID", "Attribute", "Value", "Outlier_Status", "Treatment"]
    )

    # Merge both reports
    full_report = pd.concat([iqr_df, domain_report], ignore_index=True)
    # Remove duplicates
    full_report = full_report.drop_duplicates(
        subset=["Student_ID", "Attribute", "Value"], keep="first"
    ).reset_index(drop=True)

    return full_report, iqr_results


def treat_outliers(
    df: pd.DataFrame,
    outlier_report: pd.DataFrame,
) -> pd.DataFrame:
    """Apply treatment to outliers based on the report.

    - Invalid domain values -> convert to NaN
    - Statistical outliers -> keep but flag (don't delete)

    Returns:
        Treated DataFrame
    """
    if df is None or df.empty:
        return df

    df_treated = df.copy()

    if outlier_report is not None and not outlier_report.empty:
        invalid_mask = outlier_report["Outlier_Status"].str.contains("Invalid", case=False)
        invalid_records = outlier_report[invalid_mask]

        for _, row in invalid_records.iterrows():
            sid = row["Student_ID"]
            attr = row["Attribute"]

            if attr in df_treated.columns and "Student_ID" in df_treated.columns:
                mask = df_treated["Student_ID"].astype(str) == str(sid)
                df_treated.loc[mask, attr] = np.nan

    return df_treated
