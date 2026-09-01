"""
Data Cleaner Module
Handles missing values, duplicates, type corrections, and text standardization.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


# Department standardization mapping
DEPARTMENT_MAP = {
    "cse": "CSE",
    "cs&e": "CSE",
    "c.s.e": "CSE",
    "computer science": "CSE",
    "ece": "ECE",
    "e.c.e": "ECE",
    "electronics": "ECE",
    "ec": "ECE",
    "eee": "EEE",
    "e.e.e": "EEE",
    "electrical": "EEE",
    "ee": "EEE",
    "mech": "MECH",
    "m.e.c.h": "MECH",
    "mechanical": "MECH",
    "civil": "CIVIL",
    "c.i.v.i.l": "CIVIL",
    "cvl": "CIVIL",
    "it": "IT",
    "i.t": "IT",
    "information technology": "IT",
}


def standardize_department(dept: str) -> str:
    """Standardize a department name to its canonical form."""
    if pd.isna(dept) or not isinstance(dept, str) or dept.strip() == "":
        return dept
    cleaned = dept.strip().lower().replace(" ", "")
    return DEPARTMENT_MAP.get(cleaned, dept.strip().upper())


def standardize_name(name: str) -> str:
    """Standardize a person's name.
    - Strip leading/trailing spaces
    - Remove special characters (keep letters, spaces, hyphens, apostrophes)
    - Normalize multiple spaces
    - Title case
    """
    if pd.isna(name) or not isinstance(name, str) or name.strip() == "":
        return name

    import re
    # Remove special characters except letters, spaces, hyphens, apostrophes
    cleaned = re.sub(r"[^a-zA-Z\s\-']", "", name)
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Title case
    cleaned = cleaned.title()
    return cleaned


def clean_missing_values(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Handle missing values in the dataset.

    - Numerical columns: median imputation
    - Categorical columns: mode imputation (or 'Unknown' if no mode)

    Returns:
        Tuple of (cleaned DataFrame, treatment report DataFrame)
    """
    if df is None or df.empty:
        return df, pd.DataFrame()

    df_clean = df.copy()
    treatments = []

    for col in df_clean.columns:
        missing_before = int(df_clean[col].isnull().sum())
        if missing_before == 0:
            continue

        if pd.api.types.is_numeric_dtype(df_clean[col]):
            median_val = pd.to_numeric(df_clean[col], errors="coerce").median()
            if pd.isna(median_val):
                df_clean[col] = df_clean[col].fillna("Unknown")
                treatment = "Filled with 'Unknown' (all values non-numeric)"
            else:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(median_val)
                treatment = f"Median imputation ({median_val:.2f})"
        else:
            mode_vals = df_clean[col].mode()
            if len(mode_vals) > 0 and pd.notna(mode_vals.iloc[0]):
                df_clean[col] = df_clean[col].fillna(mode_vals.iloc[0])
                treatment = f"Mode imputation ({mode_vals.iloc[0]})"
            else:
                df_clean[col] = df_clean[col].fillna("Unknown")
                treatment = "Filled with 'Unknown' (no mode found)"

        missing_after = int(df_clean[col].isnull().sum())
        treatments.append({
            "Column": col,
            "Missing Before": missing_before,
            "Treatment": treatment,
            "Missing After": missing_after,
        })

    return df_clean, pd.DataFrame(treatments)


def handle_duplicates(df: pd.DataFrame, unique_id_required: bool = True) -> Tuple[pd.DataFrame, Dict]:
    """Detect and handle duplicate records.

    Args:
        df: DataFrame to deduplicate
        unique_id_required: If True, enforce unique Student_ID (for student-level datasets
                            like admission/placement). If False, only remove exact duplicate
                            rows (for multi-record datasets like examination/registration/attendance).

    Returns:
        Tuple of (cleaned DataFrame, duplicate info dictionary)
    """
    if df is None or df.empty:
        return df, {}

    df_clean = df.copy()
    info = {
        "exact_duplicates": int(df_clean.duplicated().sum()),
        "total_rows_before": len(df_clean),
    }

    # Remove exact duplicate rows
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    info["total_rows_after_dedup"] = len(df_clean)

    # For student-level datasets, enforce unique Student_ID
    if unique_id_required and "Student_ID" in df_clean.columns:
        dup_ids = df_clean[df_clean.duplicated(subset=["Student_ID"], keep=False)]
        info["duplicate_student_ids"] = len(dup_ids)
        info["unique_duplicate_ids"] = dup_ids["Student_ID"].nunique() if len(dup_ids) > 0 else 0
        # Keep first occurrence for now
        df_clean = df_clean.drop_duplicates(subset=["Student_ID"], keep="first").reset_index(drop=True)
    elif not unique_id_required and "Student_ID" in df_clean.columns:
        # Still report but don't remove — multiple records per student are valid
        dup_ids = df_clean[df_clean.duplicated(subset=["Student_ID"], keep=False)]
        info["duplicate_student_ids"] = len(dup_ids)
        info["unique_duplicate_ids"] = dup_ids["Student_ID"].nunique() if len(dup_ids) > 0 else 0
        info["note"] = "Multiple records per Student_ID are valid for this dataset type"

    info["total_rows_final"] = len(df_clean)
    return df_clean, info


def correct_data_types(df: pd.DataFrame, dataset_type: str = "") -> pd.DataFrame:
    """Automatically correct data types based on column names and content.

    Args:
        df: DataFrame to correct
        dataset_type: Hint about which dataset this is (admission, examination, etc.)
    """
    if df is None or df.empty:
        return df

    df_clean = df.copy()

    # Student_ID -> string
    if "Student_ID" in df_clean.columns:
        df_clean["Student_ID"] = df_clean["Student_ID"].astype(str).str.strip()

    # Numerical corrections
    numeric_cols = ["Marks", "Attendance", "Credits", "Package_LPA", "CGPA"]
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Integer columns
    int_cols = ["Semester", "Admission_Year"]
    for col in int_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").astype("Int64")

    # String columns
    str_cols = ["Name", "Gender", "Department", "Email", "Course", "Grade",
                "Placement_Status", "Company"]
    for col in str_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()

    return df_clean


def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize all text fields in the dataset."""
    if df is None or df.empty:
        return df

    df_clean = df.copy()

    # Standardize names
    if "Name" in df_clean.columns:
        df_clean["Name"] = df_clean["Name"].apply(standardize_name)

    # Standardize departments
    if "Department" in df_clean.columns:
        df_clean["Department"] = df_clean["Department"].apply(standardize_department)

    # Standardize course names (title case, strip)
    if "Course" in df_clean.columns:
        df_clean["Course"] = df_clean["Course"].apply(
            lambda x: x.strip().title() if pd.notna(x) and isinstance(x, str) else x
        )

    # Standardize grades
    if "Grade" in df_clean.columns:
        df_clean["Grade"] = df_clean["Grade"].apply(
            lambda x: x.strip().upper() if pd.notna(x) and isinstance(x, str) else x
        )

    # Standardize placement status
    if "Placement_Status" in df_clean.columns:
        df_clean["Placement_Status"] = df_clean["Placement_Status"].apply(
            lambda x: x.strip().title() if pd.notna(x) and isinstance(x, str) else x
        )

    # Standardize email (lowercase)
    if "Email" in df_clean.columns:
        df_clean["Email"] = df_clean["Email"].apply(
            lambda x: x.strip().lower() if pd.notna(x) and isinstance(x, str) else x
        )

    # Standardize gender
    if "Gender" in df_clean.columns:
        df_clean["Gender"] = df_clean["Gender"].apply(
            lambda x: x.strip().title() if pd.notna(x) and isinstance(x, str) else x
        )

    return df_clean


# Datasets where Student_ID should be unique (one row per student)
UNIQUE_ID_DATASETS = {"admission", "placement"}


def full_clean_pipeline(df: pd.DataFrame, dataset_type: str = "") -> Tuple[pd.DataFrame, Dict]:
    """Run the full cleaning pipeline on a dataset.

    Args:
        df: The DataFrame to clean
        dataset_type: Dataset name hint (e.g., 'admission', 'examination')

    Returns:
        Tuple of (cleaned DataFrame, cleaning report dictionary)
    """
    if df is None or df.empty:
        return df, {"error": "Dataset is empty"}

    report = {"steps": []}

    # Determine if Student_ID should be unique for this dataset
    unique_id_required = dataset_type.lower() in UNIQUE_ID_DATASETS

    # Step 1: Correct data types
    df_clean = correct_data_types(df, dataset_type)
    report["steps"].append("Data type correction")

    # Step 2: Standardize text
    df_clean = standardize_text(df_clean)
    report["steps"].append("Text standardization")

    # Step 3: Handle missing values
    df_clean, treatment_df = clean_missing_values(df_clean)
    report["steps"].append("Missing value treatment")
    report["treatment_report"] = treatment_df

    # Step 4: Handle duplicates
    df_clean, dup_info = handle_duplicates(df_clean, unique_id_required=unique_id_required)
    report["steps"].append("Duplicate handling")
    report["duplicate_info"] = dup_info

    report["rows_before"] = len(df)
    report["rows_after"] = len(df_clean)
    report["columns"] = len(df_clean.columns)

    return df_clean, report
