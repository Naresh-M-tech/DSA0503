"""
Visualizer Module
Creates static visualizations using Matplotlib.
"""
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import os
from typing import Optional


# Color palette
COLORS = ["#2196F3", "#FF9800", "#4CAF50", "#E91E63", "#9C27B0",
          "#00BCD4", "#FF5722", "#795548", "#607D8B", "#CDDC39"]

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "charts")


def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_chart(fig, filename: str) -> str:
    """Save a matplotlib figure to the output/charts directory."""
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(filepath, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return filepath


def plot_marks_distribution(df: pd.DataFrame) -> Optional[str]:
    """Histogram of Marks distribution."""
    if "Marks" not in df.columns:
        return None

    marks = pd.to_numeric(df["Marks"], errors="coerce").dropna()
    if marks.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(marks, bins=20, color=COLORS[0], edgecolor="white", alpha=0.85)
    ax.set_title("Marks Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Marks", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.grid(axis="y", alpha=0.3)
    ax.axvline(marks.mean(), color="red", linestyle="--", linewidth=1.5,
               label=f"Mean: {marks.mean():.1f}")
    ax.legend(fontsize=10)
    plt.tight_layout()
    return save_chart(fig, "marks_distribution.png")


def plot_cgpa_distribution(df: pd.DataFrame) -> Optional[str]:
    """Histogram of CGPA distribution."""
    if "CGPA" not in df.columns:
        return None

    cgpa = pd.to_numeric(df["CGPA"], errors="coerce").dropna()
    if cgpa.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(cgpa, bins=15, color=COLORS[2], edgecolor="white", alpha=0.85)
    ax.set_title("CGPA Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("CGPA", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.grid(axis="y", alpha=0.3)
    ax.axvline(cgpa.mean(), color="red", linestyle="--", linewidth=1.5,
               label=f"Mean: {cgpa.mean():.2f}")
    ax.legend(fontsize=10)
    plt.tight_layout()
    return save_chart(fig, "cgpa_distribution.png")


def plot_department_avg_marks(df: pd.DataFrame) -> Optional[str]:
    """Bar chart of department-wise average marks."""
    if "Department" not in df.columns or "Marks" not in df.columns:
        return None

    dept_avg = df.groupby("Department")["Marks"].apply(
        lambda x: pd.to_numeric(x, errors="coerce").mean()
    ).dropna().sort_values(ascending=True)

    if dept_avg.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(dept_avg.index, dept_avg.values, color=COLORS[:len(dept_avg)])
    ax.set_title("Department-wise Average Marks", fontsize=14, fontweight="bold")
    ax.set_xlabel("Average Marks", fontsize=12)
    ax.set_ylabel("Department", fontsize=12)
    ax.grid(axis="x", alpha=0.3)

    for bar, val in zip(bars, dept_avg.values):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=10)

    plt.tight_layout()
    return save_chart(fig, "department_avg_marks.png")


def plot_course_avg_marks(df: pd.DataFrame) -> Optional[str]:
    """Bar chart of course-wise average marks."""
    if "Course" not in df.columns or "Marks" not in df.columns:
        return None

    course_avg = df.groupby("Course")["Marks"].apply(
        lambda x: pd.to_numeric(x, errors="coerce").mean()
    ).dropna().sort_values(ascending=True)

    if course_avg.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(course_avg.index, course_avg.values, color=COLORS[:len(course_avg)])
    ax.set_title("Course-wise Average Marks", fontsize=14, fontweight="bold")
    ax.set_xlabel("Average Marks", fontsize=12)
    ax.set_ylabel("Course", fontsize=12)
    ax.grid(axis="x", alpha=0.3)

    for bar, val in zip(bars, course_avg.values):
        ax.text(val + 0.3, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}", va="center", fontsize=9)

    plt.tight_layout()
    return save_chart(fig, "course_avg_marks.png")


def plot_attendance_vs_marks(df: pd.DataFrame) -> Optional[str]:
    """Scatter plot of Attendance vs Marks."""
    if "Attendance" not in df.columns or "Marks" not in df.columns:
        return None

    att = pd.to_numeric(df["Attendance"], errors="coerce")
    marks = pd.to_numeric(df["Marks"], errors="coerce")
    valid = att.notna() & marks.notna()

    if valid.sum() == 0:
        return None

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(att[valid], marks[valid], alpha=0.5, color=COLORS[0], s=30, edgecolors="white")

    # Add trend line
    z = np.polyfit(att[valid], marks[valid], 1)
    p = np.poly1d(z)
    x_line = np.linspace(att[valid].min(), att[valid].max(), 100)
    ax.plot(x_line, p(x_line), color="red", linestyle="--", linewidth=1.5,
            label=f"Trend (slope: {z[0]:.2f})")

    ax.set_title("Attendance vs Marks", fontsize=14, fontweight="bold")
    ax.set_xlabel("Attendance (%)", fontsize=12)
    ax.set_ylabel("Marks", fontsize=12)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10)
    plt.tight_layout()
    return save_chart(fig, "attendance_vs_marks.png")


def plot_semester_performance(df: pd.DataFrame) -> Optional[str]:
    """Line chart of semester-wise average performance."""
    if "Semester" not in df.columns or "Marks" not in df.columns:
        return None

    df_valid = df.dropna(subset=["Semester"])
    df_valid["Semester"] = pd.to_numeric(df_valid["Semester"], errors="coerce")
    df_valid = df_valid.dropna(subset=["Semester"])

    if df_valid.empty:
        return None

    sem_avg = df_valid.groupby("Semester").agg(
        Avg_Marks=("Marks", lambda x: pd.to_numeric(x, errors="coerce").mean()),
        Avg_Attendance=("Attendance", lambda x: pd.to_numeric(x, errors="coerce").mean())
    ).dropna()

    if sem_avg.empty:
        return None

    fig, ax1 = plt.subplots(figsize=(9, 5))

    ax1.plot(sem_avg.index, sem_avg["Avg_Marks"], marker="o",
             color=COLORS[0], linewidth=2, label="Avg Marks")
    ax1.set_xlabel("Semester", fontsize=12)
    ax1.set_ylabel("Average Marks", fontsize=12, color=COLORS[0])
    ax1.tick_params(axis="y", labelcolor=COLORS[0])

    if "Avg_Attendance" in sem_avg.columns and sem_avg["Avg_Attendance"].notna().any():
        ax2 = ax1.twinx()
        ax2.plot(sem_avg.index, sem_avg["Avg_Attendance"], marker="s",
                 color=COLORS[1], linewidth=2, linestyle="--", label="Avg Attendance")
        ax2.set_ylabel("Average Attendance (%)", fontsize=12, color=COLORS[1])
        ax2.tick_params(axis="y", labelcolor=COLORS[1])
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)
    else:
        ax1.legend(fontsize=10)

    ax1.set_title("Semester-wise Performance Trend", fontsize=14, fontweight="bold")
    ax1.grid(alpha=0.3)
    ax1.set_xticks(sem_avg.index)
    plt.tight_layout()
    return save_chart(fig, "semester_performance.png")


def plot_department_attendance(df: pd.DataFrame) -> Optional[str]:
    """Bar chart of department-wise average attendance."""
    if "Department" not in df.columns or "Attendance" not in df.columns:
        return None

    dept_att = df.groupby("Department")["Attendance"].apply(
        lambda x: pd.to_numeric(x, errors="coerce").mean()
    ).dropna().sort_values(ascending=False)

    if dept_att.empty:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(dept_att.index, dept_att.values, color=COLORS[:len(dept_att)], edgecolor="white")
    ax.set_title("Department-wise Average Attendance", fontsize=14, fontweight="bold")
    ax.set_xlabel("Department", fontsize=12)
    ax.set_ylabel("Average Attendance (%)", fontsize=12)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 105)

    for bar, val in zip(bars, dept_att.values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                f"{val:.1f}%", ha="center", fontsize=10)

    plt.tight_layout()
    return save_chart(fig, "department_attendance.png")


def plot_placement_status(df: pd.DataFrame) -> Optional[str]:
    """Pie/bar chart of placement status."""
    if "Placement_Status" not in df.columns:
        return None

    status_counts = df["Placement_Status"].value_counts()
    # Filter out non-valid statuses
    valid_statuses = status_counts[status_counts.index.isin(["Placed", "Not Placed"])]

    if valid_statuses.empty:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart
    bars = ax1.bar(valid_statuses.index, valid_statuses.values,
                   color=[COLORS[2], COLORS[3]], edgecolor="white")
    ax1.set_title("Placement Status (Bar)", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Number of Students", fontsize=11)
    ax1.grid(axis="y", alpha=0.3)

    for bar, val in zip(bars, valid_statuses.values):
        ax1.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                 str(val), ha="center", fontsize=11, fontweight="bold")

    # Pie chart
    ax2.pie(valid_statuses.values, labels=valid_statuses.index,
            colors=[COLORS[2], COLORS[3]], autopct="%1.1f%%",
            startangle=90, textprops={"fontsize": 11})
    ax2.set_title("Placement Status (Pie)", fontsize=13, fontweight="bold")

    plt.tight_layout()
    return save_chart(fig, "placement_status.png")


def generate_all_charts(df: pd.DataFrame) -> dict:
    """Generate all static charts and return their file paths."""
    charts = {}

    chart_funcs = [
        ("Marks Distribution", plot_marks_distribution),
        ("CGPA Distribution", plot_cgpa_distribution),
        ("Department Average Marks", plot_department_avg_marks),
        ("Course Average Marks", plot_course_avg_marks),
        ("Attendance vs Marks", plot_attendance_vs_marks),
        ("Semester Performance", plot_semester_performance),
        ("Department Attendance", plot_department_attendance),
        ("Placement Status", plot_placement_status),
    ]

    for name, func in chart_funcs:
        try:
            path = func(df)
            if path:
                charts[name] = path
        except Exception as e:
            print(f"Warning: Could not generate '{name}': {e}")

    return charts
