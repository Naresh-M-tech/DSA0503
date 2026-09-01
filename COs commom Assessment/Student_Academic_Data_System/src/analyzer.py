"""
Analyzer Module
Performs statistical analysis on the integrated student academic dataset.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def compute_basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute basic statistical measures for key academic fields."""
    stats = {}

    for col in ["Marks", "Attendance", "CGPA", "Package_LPA", "Credits"]:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce")
            valid = series.dropna()
            if len(valid) > 0:
                stats[col] = {
                    "mean": round(float(valid.mean()), 2),
                    "median": round(float(valid.median()), 2),
                    "std": round(float(valid.std()), 2),
                    "min": round(float(valid.min()), 2),
                    "max": round(float(valid.max()), 2),
                    "count": int(len(valid)),
                }
            else:
                stats[col] = {"mean": None, "median": None, "std": None,
                              "min": None, "max": None, "count": 0}

    return stats


def department_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze performance by department."""
    if "Department" not in df.columns:
        return pd.DataFrame()

    dept_groups = df.groupby("Department")

    results = []
    for dept, group in dept_groups:
        if pd.isna(dept) or str(dept).strip() == "" or str(dept).lower() == "nan":
            continue

        row = {"Department": dept, "Student_Count": len(group)}

        for col in ["Marks", "Attendance", "CGPA"]:
            if col in group.columns:
                vals = pd.to_numeric(group[col], errors="coerce").dropna()
                if len(vals) > 0:
                    row[f"Avg_{col}"] = round(float(vals.mean()), 2)
                else:
                    row[f"Avg_{col}"] = None

        if "Placement_Status" in group.columns:
            placed = group[group["Placement_Status"] == "Placed"]
            total = group[group["Placement_Status"].isin(["Placed", "Not Placed"])]
            row["Placement_%"] = round(
                (len(placed) / len(total) * 100) if len(total) > 0 else 0, 1
            )
        else:
            row["Placement_%"] = None

        results.append(row)

    return pd.DataFrame(results)


def course_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze performance by course."""
    if "Course" not in df.columns:
        return pd.DataFrame()

    course_groups = df.groupby("Course")

    results = []
    for course, group in course_groups:
        if pd.isna(course) or str(course).strip() == "" or str(course).lower() == "nan":
            continue

        row = {"Course": course, "Student_Count": len(group)}

        if "Marks" in group.columns:
            vals = pd.to_numeric(group["Marks"], errors="coerce").dropna()
            if len(vals) > 0:
                row["Avg_Marks"] = round(float(vals.mean()), 2)
                row["Min_Marks"] = round(float(vals.min()), 2)
                row["Max_Marks"] = round(float(vals.max()), 2)
            else:
                row["Avg_Marks"] = None
                row["Min_Marks"] = None
                row["Max_Marks"] = None

        if "Attendance" in group.columns:
            vals = pd.to_numeric(group["Attendance"], errors="coerce").dropna()
            if len(vals) > 0:
                row["Avg_Attendance"] = round(float(vals.mean()), 2)
            else:
                row["Avg_Attendance"] = None

        results.append(row)

    return pd.DataFrame(results)


def semester_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze performance by semester."""
    if "Semester" not in df.columns:
        return pd.DataFrame()

    df_valid = df.dropna(subset=["Semester"])
    sem_groups = df_valid.groupby("Semester")

    results = []
    for sem, group in sem_groups:
        row = {"Semester": int(sem) if pd.notna(sem) else sem}

        for col in ["Marks", "Attendance", "CGPA"]:
            if col in group.columns:
                vals = pd.to_numeric(group[col], errors="coerce").dropna()
                if len(vals) > 0:
                    row[f"Avg_{col}"] = round(float(vals.mean()), 2)
                else:
                    row[f"Avg_{col}"] = None

        results.append(row)

    return pd.DataFrame(results).sort_values("Semester")


def placement_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze placement data."""
    if "Placement_Status" not in df.columns:
        return {"error": "Placement_Status column not found"}

    placed = df[df["Placement_Status"] == "Placed"]
    not_placed = df[df["Placement_Status"] == "Not Placed"]
    total_with_status = df[df["Placement_Status"].isin(["Placed", "Not Placed"])]

    result = {
        "total_students": len(df),
        "placed_count": len(placed),
        "not_placed_count": len(not_placed),
        "placement_percentage": round(
            (len(placed) / len(total_with_status) * 100) if len(total_with_status) > 0 else 0, 1
        ),
    }

    for col in ["Marks", "CGPA", "Attendance"]:
        if col in df.columns:
            placed_vals = pd.to_numeric(placed[col], errors="coerce").dropna()
            not_placed_vals = pd.to_numeric(not_placed[col], errors="coerce").dropna()
            result[f"avg_{col}_placed"] = round(float(placed_vals.mean()), 2) if len(placed_vals) > 0 else None
            result[f"avg_{col}_not_placed"] = round(float(not_placed_vals.mean()), 2) if len(not_placed_vals) > 0 else None

    # Department-wise placement
    if "Department" in df.columns:
        dept_placement = []
        for dept in df["Department"].dropna().unique():
            dept_df = df[df["Department"] == dept]
            dept_placed = dept_df[dept_df["Placement_Status"] == "Placed"]
            dept_total = dept_df[dept_df["Placement_Status"].isin(["Placed", "Not Placed"])]
            if len(dept_total) > 0:
                dept_placement.append({
                    "Department": dept,
                    "Total": len(dept_total),
                    "Placed": len(dept_placed),
                    "Placement_%": round(len(dept_placed) / len(dept_total) * 100, 1),
                })
        result["department_placement"] = pd.DataFrame(dept_placement)

    return result


def attendance_marks_correlation(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate correlation between attendance and marks."""
    if "Attendance" not in df.columns or "Marks" not in df.columns:
        return {"error": "Attendance or Marks column not found"}

    att = pd.to_numeric(df["Attendance"], errors="coerce")
    marks = pd.to_numeric(df["Marks"], errors="coerce")

    valid_mask = att.notna() & marks.notna()
    correlation = att[valid_mask].corr(marks[valid_mask])

    if pd.isna(correlation):
        interpretation = "Insufficient data to calculate correlation"
    elif abs(correlation) >= 0.7:
        interpretation = f"Strong {'positive' if correlation > 0 else 'negative'} correlation"
    elif abs(correlation) >= 0.4:
        interpretation = f"Moderate {'positive' if correlation > 0 else 'negative'} correlation"
    elif abs(correlation) >= 0.2:
        interpretation = f"Weak {'positive' if correlation > 0 else 'negative'} correlation"
    else:
        interpretation = "Very weak or no correlation"

    return {
        "correlation": round(float(correlation), 4) if pd.notna(correlation) else None,
        "interpretation": interpretation,
        "valid_pairs": int(valid_mask.sum()),
    }


def low_performing_courses(df: pd.DataFrame, threshold: float = 60.0) -> pd.DataFrame:
    """Identify courses with average marks below threshold."""
    courses = course_analysis(df)
    if courses.empty or "Avg_Marks" not in courses.columns:
        return pd.DataFrame()

    low = courses[courses["Avg_Marks"] < threshold].sort_values("Avg_Marks")
    return low


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute key performance indicators for the dashboard."""
    kpis = {
        "total_students": 0,
        "avg_marks": 0,
        "avg_cgpa": 0,
        "avg_attendance": 0,
        "students_needing_support": 0,
        "placement_percentage": 0,
    }

    if df is None or df.empty:
        return kpis

    kpis["total_students"] = df["Student_ID"].nunique() if "Student_ID" in df.columns else len(df)

    for col, key in [("Marks", "avg_marks"), ("CGPA", "avg_cgpa"), ("Attendance", "avg_attendance")]:
        if col in df.columns:
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(vals) > 0:
                kpis[key] = round(float(vals.mean()), 2)

    # Students needing support
    if "CGPA" in df.columns:
        cgpa = pd.to_numeric(df["CGPA"], errors="coerce")
        marks = pd.to_numeric(df.get("Marks", pd.Series()), errors="coerce")
        att = pd.to_numeric(df.get("Attendance", pd.Series()), errors="coerce")

        support_mask = pd.Series(False, index=df.index)
        if not cgpa.isna().all():
            support_mask |= cgpa < 6.0
        if not marks.isna().all():
            support_mask |= marks < 50
        if not att.isna().all():
            support_mask |= att < 75

        kpis["students_needing_support"] = int(support_mask.sum())

    # Placement
    if "Placement_Status" in df.columns:
        placed = df[df["Placement_Status"] == "Placed"]
        total = df[df["Placement_Status"].isin(["Placed", "Not Placed"])]
        kpis["placement_percentage"] = round(
            (len(placed) / len(total) * 100) if len(total) > 0 else 0, 1
        )

    return kpis
