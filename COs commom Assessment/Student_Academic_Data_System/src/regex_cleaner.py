"""
Regex Cleaner Module
Validates and cleans Student IDs, Emails, and Names using regular expressions.
"""
import re
import pandas as pd
from typing import Dict, Tuple


# Regex patterns
STUDENT_ID_PATTERN = re.compile(r"^S\d{3}$")
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s\-']+[A-Za-z]$")
NAME_CLEANUP_PATTERN = re.compile(r"[^a-zA-Z\s\-']")


def validate_student_id(student_id: str) -> bool:
    """Validate a Student_ID against the expected pattern S###."""
    if pd.isna(student_id) or not isinstance(student_id, str):
        return False
    return bool(STUDENT_ID_PATTERN.match(student_id.strip()))


def validate_email(email: str) -> bool:
    """Validate an email address against a standard pattern."""
    if pd.isna(email) or not isinstance(email, str) or email.strip() == "":
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))


def validate_name(name: str) -> bool:
    """Validate a name (letters, spaces, hyphens, apostrophes only)."""
    if pd.isna(name) or not isinstance(name, str) or name.strip() == "":
        return False
    return bool(NAME_PATTERN.match(name.strip()))


def clean_student_id(student_id: str) -> str:
    """Try to clean a Student_ID to match the S### format."""
    if pd.isna(student_id) or not isinstance(student_id, str):
        return str(student_id)
    cleaned = student_id.strip()
    # Remove any non-alphanumeric characters except the leading S
    match = re.search(r"S\d+", cleaned, re.IGNORECASE)
    if match:
        num_part = re.search(r"\d+", match.group())
        if num_part:
            return f"S{num_part.group().zfill(3)}"
    return cleaned


def clean_name_regex(name: str) -> str:
    """Clean a name using regex: remove unwanted characters, normalize whitespace."""
    if pd.isna(name) or not isinstance(name, str):
        return str(name)
    # Remove unwanted characters
    cleaned = NAME_CLEANUP_PATTERN.sub("", name)
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # Title case
    cleaned = cleaned.title()
    return cleaned


def apply_regex_validation(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply regex validation and cleaning to a DataFrame.

    Returns:
        Tuple of (cleaned DataFrame, validation report DataFrame, changes log DataFrame)
    """
    if df is None or df.empty:
        return df, pd.DataFrame(), pd.DataFrame()

    df_clean = df.copy()
    validation_rows = []
    changes = []

    # Validate Student_ID
    if "Student_ID" in df_clean.columns:
        total = len(df_clean)
        valid = 0
        invalid = 0
        for idx in df_clean.index:
            sid = df_clean.at[idx, "Student_ID"]
            original = str(sid)
            if validate_student_id(str(sid)):
                valid += 1
            else:
                invalid += 1
                new_id = clean_student_id(str(sid))
                if new_id != original:
                    df_clean.at[idx, "Student_ID"] = new_id
                    changes.append({
                        "Field": "Student_ID",
                        "Original": original,
                        "Cleaned": new_id,
                        "Row": idx,
                    })

        validation_rows.append({
            "Field": "Student_ID",
            "Total": total,
            "Valid": valid,
            "Invalid": invalid,
        })

    # Validate Email
    if "Email" in df_clean.columns:
        total = len(df_clean)
        valid = 0
        invalid = 0
        for idx in df_clean.index:
            email = df_clean.at[idx, "Email"]
            if validate_email(str(email)):
                valid += 1
            else:
                invalid += 1
                changes.append({
                    "Field": "Email",
                    "Original": str(email),
                    "Cleaned": "Flagged as invalid",
                    "Row": idx,
                })

        validation_rows.append({
            "Field": "Email",
            "Total": total,
            "Valid": valid,
            "Invalid": invalid,
        })

    # Validate Name
    if "Name" in df_clean.columns:
        total = len(df_clean)
        valid = 0
        invalid = 0
        for idx in df_clean.index:
            name = df_clean.at[idx, "Name"]
            original = str(name)
            cleaned = clean_name_regex(str(name))
            if validate_name(cleaned):
                valid += 1
            else:
                invalid += 1

            if cleaned != original and cleaned:
                df_clean.at[idx, "Name"] = cleaned
                changes.append({
                    "Field": "Name",
                    "Original": original,
                    "Cleaned": cleaned,
                    "Row": idx,
                })

        validation_rows.append({
            "Field": "Name",
            "Total": total,
            "Valid": valid,
            "Invalid": invalid,
        })

    validation_report = pd.DataFrame(validation_rows)
    changes_log = pd.DataFrame(changes) if changes else pd.DataFrame(
        columns=["Field", "Original", "Cleaned", "Row"]
    )

    return df_clean, validation_report, changes_log
