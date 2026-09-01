"""
Insights Module
Generates actionable academic insights and recommendations.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


# Default thresholds (configurable)
DEFAULT_THRESHOLDS = {
    "cgpa_low": 6.0,
    "marks_low": 50.0,
    "attendance_low": 75.0,
    "low_course_threshold": 60.0,
}


def find_students_needing_support(
    df: pd.DataFrame,
    thresholds: Dict = None,
) -> pd.DataFrame:
    """Identify students requiring academic support.

    Rules (configurable):
        - CGPA < threshold (default 6.0)
        - Average Marks < threshold (default 50.0)
        - Attendance < threshold (default 75%)

    Returns:
        DataFrame with Student_ID, Name, Department, CGPA, Marks, Attendance, Reason
    """
    if df is None or df.empty:
        return pd.DataFrame()

    t = thresholds or DEFAULT_THRESHOLDS
    support_records = []

    # Group by Student_ID to get per-student summary
    student_groups = df.groupby("Student_ID") if "Student_ID" in df.columns else [(None, df)]

    for sid, group in student_groups:
        name = group["Name"].mode().iloc[0] if "Name" in group.columns and not group["Name"].mode().empty else "Unknown"
        dept = group["Department"].mode().iloc[0] if "Department" in group.columns and not group["Department"].mode().empty else "Unknown"

        cgpa_vals = pd.to_numeric(group["CGPA"], errors="coerce").dropna()
        marks_vals = pd.to_numeric(group["Marks"], errors="coerce").dropna()
        att_vals = pd.to_numeric(group["Attendance"], errors="coerce").dropna()

        avg_cgpa = float(cgpa_vals.mean()) if len(cgpa_vals) > 0 else None
        avg_marks = float(marks_vals.mean()) if len(marks_vals) > 0 else None
        avg_att = float(att_vals.mean()) if len(att_vals) > 0 else None

        reasons = []
        if avg_cgpa is not None and avg_cgpa < t["cgpa_low"]:
            reasons.append("Low CGPA")
        if avg_marks is not None and avg_marks < t["marks_low"]:
            reasons.append("Low Marks")
        if avg_att is not None and avg_att < t["attendance_low"]:
            reasons.append("Low Attendance")

        if reasons:
            support_records.append({
                "Student_ID": sid,
                "Name": name,
                "Department": dept,
                "CGPA": round(avg_cgpa, 2) if avg_cgpa is not None else None,
                "Avg_Marks": round(avg_marks, 2) if avg_marks is not None else None,
                "Attendance": round(avg_att, 2) if avg_att is not None else None,
                "Reason": " and ".join(reasons),
            })

    result = pd.DataFrame(support_records)
    if not result.empty:
        result = result.sort_values("CGPA", ascending=True).reset_index(drop=True)
    return result


def find_low_performing_courses(
    df: pd.DataFrame,
    threshold: float = 60.0,
) -> pd.DataFrame:
    """Identify courses with low average marks.

    Returns:
        DataFrame with Course, Avg_Marks, Student_Count, Recommendations
    """
    if df is None or df.empty or "Course" not in df.columns or "Marks" not in df.columns:
        return pd.DataFrame()

    course_groups = df.groupby("Course")
    results = []

    for course, group in course_groups:
        if pd.isna(course) or str(course).strip() == "" or str(course).lower() == "nan":
            continue

        marks = pd.to_numeric(group["Marks"], errors="coerce").dropna()
        if len(marks) == 0:
            continue

        avg = float(marks.mean())
        if avg < threshold:
            recommendations = []
            if avg < 40:
                recommendations.append("Immediate faculty review recommended")
                recommendations.append("Organize remedial classes")
            elif avg < 50:
                recommendations.append("Additional tutorial sessions")
                recommendations.append("Attendance monitoring")
            else:
                recommendations.append("Supplementary practice materials")
                recommendations.append("Peer tutoring sessions")

            # Check attendance if available
            if "Attendance" in group.columns:
                att = pd.to_numeric(group["Attendance"], errors="coerce").dropna()
                if len(att) > 0 and att.mean() < 75:
                    recommendations.append("Strict attendance policy enforcement")

            results.append({
                "Course": course,
                "Avg_Marks": round(avg, 2),
                "Min_Marks": round(float(marks.min()), 2),
                "Max_Marks": round(float(marks.max()), 2),
                "Student_Count": len(marks),
                "Recommendations": "; ".join(recommendations),
            })

    return pd.DataFrame(results).sort_values("Avg_Marks") if results else pd.DataFrame()


def attendance_performance_analysis(df: pd.DataFrame) -> Dict:
    """Analyze the correlation between attendance and performance."""
    if "Attendance" not in df.columns or "Marks" not in df.columns:
        return {"error": "Required columns not found"}

    att = pd.to_numeric(df["Attendance"], errors="coerce")
    marks = pd.to_numeric(df["Marks"], errors="coerce")
    valid = att.notna() & marks.notna()

    if valid.sum() < 3:
        return {"error": "Insufficient data for correlation analysis"}

    correlation = float(att[valid].corr(marks[valid]))

    # Categorize students
    high_att = att[valid] >= 75
    low_att = att[valid] < 75

    avg_marks_high_att = float(marks[valid & high_att].mean()) if high_att.sum() > 0 else None
    avg_marks_low_att = float(marks[valid & low_att].mean()) if low_att.sum() > 0 else None

    return {
        "correlation": round(correlation, 4),
        "interpretation": _interpret_correlation(correlation),
        "high_attendance_avg_marks": round(avg_marks_high_att, 2) if avg_marks_high_att else None,
        "low_attendance_avg_marks": round(avg_marks_low_att, 2) if avg_marks_low_att else None,
        "high_attendance_count": int(high_att.sum()),
        "low_attendance_count": int(low_att.sum()),
        "valid_pairs": int(valid.sum()),
    }


def _interpret_correlation(r: float) -> str:
    """Interpret a correlation coefficient."""
    strength = "very weak"
    if abs(r) >= 0.8:
        strength = "very strong"
    elif abs(r) >= 0.6:
        strength = "strong"
    elif abs(r) >= 0.4:
        strength = "moderate"
    elif abs(r) >= 0.2:
        strength = "weak"

    direction = "positive" if r >= 0 else "negative"
    return f"{strength.title()} {direction} correlation (r={r:.3f}). Note: correlation does not imply causation."


def generate_all_insights(
    df: pd.DataFrame,
    thresholds: Dict = None,
) -> Dict:
    """Generate all academic insights.

    Returns:
        Dictionary with all insight results
    """
    insights = {
        "students_needing_support": find_students_needing_support(df, thresholds),
        "low_performing_courses": find_low_performing_courses(
            df,
            thresholds.get("low_course_threshold", 60.0) if thresholds else 60.0,
        ),
        "attendance_performance": attendance_performance_analysis(df),
    }
    return insights
