"""
Data Integrator Module
Merges all cleaned datasets into one unified student academic dataset.
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


def integrate_datasets(
    datasets: Dict[str, pd.DataFrame],
) -> Tuple[pd.DataFrame, Dict]:
    """Merge all cleaned datasets using Student_ID as the key.

    Strategy: Build a per-course-per-student record by joining examination,
    registration, and attendance on (Student_ID, Course), then add
    student-level demographics from admission and placement.

    Args:
        datasets: Dictionary mapping dataset names to DataFrames.
                  Expected keys: 'admission', 'registration', 'attendance',
                                 'examination', 'placement'

    Returns:
        Tuple of (integrated DataFrame, integration report)
    """
    report = {
        "datasets_used": list(datasets.keys()),
        "rows_before": {},
        "total_records_before": 0,
    }

    # Ensure Student_ID is string in all datasets
    for name, df in datasets.items():
        if df is not None and not df.empty and "Student_ID" in df.columns:
            df["Student_ID"] = df["Student_ID"].astype(str).str.strip()
            report["rows_before"][name] = len(df)
            report["total_records_before"] += len(df)

    # ── Step 1: Start with examination as the core per-course record ──
    if "examination" in datasets and datasets["examination"] is not None:
        base = datasets["examination"].copy()
        keep_cols = ["Student_ID", "Course", "Marks", "Grade", "Semester"]
        base = base[[c for c in keep_cols if c in base.columns]]
    else:
        # No examination data; try registration
        if "registration" in datasets and datasets["registration"] is not None:
            base = datasets["registration"].copy()
            keep_cols = ["Student_ID", "Course", "Credits", "Semester"]
            base = base[[c for c in keep_cols if c in base.columns]]
        else:
            # Fallback: just create from first available dataset
            for name, df in datasets.items():
                if df is not None and not df.empty and "Student_ID" in df.columns:
                    base = df[["Student_ID"]].drop_duplicates().copy()
                    break
            else:
                return pd.DataFrame(), {"error": "No datasets available for integration"}

    # ── Step 2: Merge registration data (Credits, per-course info) ──
    if "registration" in datasets and datasets["registration"] is not None:
        reg = datasets["registration"].copy()
        reg_cols = ["Student_ID", "Course", "Credits", "Semester"]
        reg = reg[[c for c in reg_cols if c in reg.columns]]

        if "Course" in base.columns and "Course" in reg.columns:
            # Merge on Student_ID + Course to get credits
            merge_on = ["Student_ID", "Course"]
            existing = set(base.columns) - {"Student_ID", "Course"}
            new_from_reg = [c for c in ["Credits"] if c in reg.columns and c not in existing]
            if new_from_reg:
                base = base.merge(
                    reg[merge_on + new_from_reg].drop_duplicates(subset=merge_on),
                    on=merge_on, how="left"
                )
        else:
            # Fallback: merge only on Student_ID for Credits
            if "Credits" in reg.columns and "Credits" not in base.columns:
                credits_avg = reg.groupby("Student_ID")["Credits"].mean().reset_index()
                credits_avg.columns = ["Student_ID", "Credits"]
                base = base.merge(credits_avg, on="Student_ID", how="left")

    # ── Step 3: Merge attendance (average per student) ──
    if "attendance" in datasets and datasets["attendance"] is not None:
        att = datasets["attendance"].copy()
        if "Attendance" in att.columns:
            att["Attendance"] = pd.to_numeric(att["Attendance"], errors="coerce")
            # Average attendance per student across all courses
            att_avg = att.groupby("Student_ID")["Attendance"].mean().reset_index()
            att_avg.columns = ["Student_ID", "Attendance"]
            base = base.merge(att_avg, on="Student_ID", how="left")

    # ── Step 4: Add student demographics from admission ──
    if "admission" in datasets and datasets["admission"] is not None:
        adm = datasets["admission"].copy()
        adm_cols = ["Student_ID", "Name", "Gender", "Department", "Email", "Admission_Year"]
        adm = adm[[c for c in adm_cols if c in adm.columns]]
        # Merge demographics onto each row
        base = base.merge(adm.drop_duplicates(subset=["Student_ID"]),
                          on="Student_ID", how="left")

    # ── Step 5: Add placement data ──
    if "placement" in datasets and datasets["placement"] is not None:
        place = datasets["placement"].copy()
        place_cols = ["Student_ID", "Placement_Status", "Company", "Package_LPA"]
        place = place[[c for c in place_cols if c in place.columns]]
        base = base.merge(place.drop_duplicates(subset=["Student_ID"]),
                          on="Student_ID", how="left")

    # ── Step 6: Calculate per-student CGPA from Marks ──
    if "Marks" in base.columns:
        # Compute CGPA as average marks / 10 per student
        marks_numeric = pd.to_numeric(base["Marks"], errors="coerce")
        student_avg_marks = base.assign(_marks=marks_numeric).groupby("Student_ID")["_marks"].transform("mean")
        base["CGPA"] = (student_avg_marks / 10).round(2).clip(0, 10)
    elif "CGPA" not in base.columns:
        base["CGPA"] = np.nan

    # ── Step 7: Fill Placement_Status for students not in placement data ──
    if "Placement_Status" in base.columns:
        base["Placement_Status"] = base["Placement_Status"].fillna("Not Listed")

    # Ensure standard column order
    desired_order = [
        "Student_ID", "Name", "Department", "Email", "Gender", "Admission_Year",
        "Course", "Credits", "Semester", "Attendance", "Marks", "Grade", "CGPA",
        "Placement_Status", "Company", "Package_LPA"
    ]
    ordered = [c for c in desired_order if c in base.columns]
    remaining = [c for c in base.columns if c not in ordered]
    base = base[ordered + remaining]

    report["rows_after"] = len(base)
    report["columns"] = list(base.columns)
    report["total_columns"] = len(base.columns)

    return base, report
