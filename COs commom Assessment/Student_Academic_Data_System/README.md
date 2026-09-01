# 🎓 Student Academic Performance Data Wrangling and Visualization System

## 1. Problem Statement

Universities store student information across multiple independent datasets — admission records, course registrations, attendance logs, examination results, and placement data. These datasets often contain quality issues such as missing values, duplicate records, inconsistent names, invalid data, and formatting differences. This project provides a comprehensive system to import, examine, clean, standardize, integrate, analyze, visualize, and report on student academic data.

## 2. Objectives

- Import datasets in CSV, JSON, and XML formats
- Profile and examine data quality across all datasets
- Clean missing values using intelligent imputation
- Detect and handle duplicates (exact rows and conflicting IDs)
- Standardize text fields (names, departments, courses)
- Validate data using regex patterns (Student ID, Email, Names)
- Identify inconsistent names using fuzzy matching (RapidFuzz)
- Detect statistical outliers (IQR method) and domain rule violations
- Integrate all cleaned datasets into a unified academic record
- Perform comprehensive statistical analysis
- Generate static visualizations (Matplotlib) and interactive charts (Plotly)
- Produce actionable academic insights and recommendations

## 3. Features

- **Multi-format Import**: CSV, JSON, XML with automatic file type detection
- **Data Profiling**: Comprehensive data quality reports per dataset
- **Intelligent Cleaning**: Median/mode imputation, type correction, text standardization
- **Regex Validation**: Student ID, Email, and Name pattern validation
- **Fuzzy Matching**: Detect inconsistent names with configurable similarity threshold
- **Outlier Detection**: IQR-based statistical detection + domain rule validation
- **Data Integration**: Merge all datasets on Student_ID into a unified record
- **Statistical Analysis**: Department, course, semester, and placement analysis
- **8 Static Charts**: Histograms, bar charts, scatter plots, line charts
- **4 Interactive Tabs**: Plotly-powered interactive visualizations with filters
- **Academic Insights**: At-risk student identification, low-performing course detection
- **Downloadable Reports**: CSV export for cleaned data, outlier reports, quality reports

## 4. Technologies

| Technology | Purpose |
|------------|---------|
| Python 3 | Core language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical operations |
| Matplotlib | Static visualizations |
| Streamlit | Web dashboard |
| Plotly | Interactive visualizations |
| RapidFuzz | Fuzzy string matching |
| lxml / ElementTree | XML processing |
| re | Regular expression validation |
| Scikit-learn | (Available if needed) |

## 5. Folder Structure

```
Student_Academic_Data_System/
├── app.py                          # Main Streamlit dashboard
├── generate_data.py                # Sample data generator
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── data/
│   ├── admission.csv               # Admission records
│   ├── registration.json           # Course registration records
│   ├── attendance.xml              # Attendance records
│   ├── examination.csv             # Examination records
│   └── placement.json              # Placement records
├── src/
│   ├── __init__.py
│   ├── data_loader.py              # CSV, JSON, XML loading
│   ├── data_profiler.py            # Data examination and profiling
│   ├── data_cleaner.py             # Missing values, duplicates, text standardization
│   ├── regex_cleaner.py            # Regex validation
│   ├── fuzzy_matcher.py            # Fuzzy name matching
│   ├── outlier_detector.py         # Outlier detection (IQR + domain rules)
│   ├── data_integrator.py          # Dataset integration
│   ├── analyzer.py                 # Statistical analysis
│   ├── visualizer.py               # Matplotlib visualizations
│   └── insights.py                 # Academic insights engine
└── output/
    ├── cleaned_data.csv            # Output cleaned data
    ├── quality_report.csv          # Data quality report
    ├── fuzzy_matching_report.csv   # Fuzzy matching results
    ├── outlier_report.csv          # Outlier detection report
    └── charts/                     # Generated chart images
```

## 6. Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd Student_Academic_Data_System
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Generate sample data (optional — the app can load it automatically):
   ```bash
   python generate_data.py
   ```

## 7. How to Run

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

### Usage

1. **Load Data**: Click "Load Sample Data" in the sidebar, or upload your own CSV/JSON/XML files
2. **Examine**: Use "Data Examination" to profile datasets
3. **Clean**: Run the full cleaning pipeline from "Data Cleaning"
4. **Fuzzy Match**: Identify inconsistent names from "Fuzzy Matching"
5. **Outliers**: Detect anomalies from "Outlier Analysis"
6. **Integrate**: Merge all datasets from "Integrated Dataset"
7. **Visualize**: Generate static charts and interactive plots
8. **Insights**: Review academic recommendations from "Academic Insights"
9. **Download**: Export reports from "Download Reports"

## 8. Dataset Format

### Admission (CSV)
| Field | Type | Description |
|-------|------|-------------|
| Student_ID | String | Format: S### (e.g., S001) |
| Name | String | Student full name |
| Gender | String | Male / Female |
| Department | String | CSE, ECE, EEE, MECH, CIVIL, IT |
| Email | String | Valid email address |
| Admission_Year | Integer | Year of admission |

### Registration (JSON)
| Field | Type | Description |
|-------|------|-------------|
| Student_ID | String | Student identifier |
| Course | String | Course name |
| Credits | Integer | Course credits |
| Semester | Integer | Semester number |

### Attendance (XML)
| Field | Type | Description |
|-------|------|-------------|
| Student_ID | String | Student identifier |
| Course | String | Course name |
| Attendance | Float | Attendance percentage (0-100) |

### Examination (CSV)
| Field | Type | Description |
|-------|------|-------------|
| Student_ID | String | Student identifier |
| Course | String | Course name |
| Marks | Float | Marks obtained (0-100) |
| Grade | String | Letter grade |
| Semester | Integer | Semester number |

### Placement (JSON)
| Field | Type | Description |
|-------|------|-------------|
| Student_ID | String | Student identifier |
| Placement_Status | String | Placed / Not Placed |
| Company | String | Company name |
| Package_LPA | Float | Package in Lakhs Per Annum |

## 9. Data Wrangling Methodology

### 9.1 Missing Value Treatment
- **Numerical columns**: Median imputation (robust to outliers)
- **Categorical columns**: Mode imputation, or "Unknown" if no mode exists
- Before/after comparison table provided

### 9.2 Duplicate Handling
- Exact duplicate rows: Identified and removed
- Duplicate Student_IDs: Detected separately; first occurrence retained
- Conflicting records reported, not silently deleted

### 9.3 Data Type Correction
- Automatic detection and conversion of column types
- Numeric columns coerced with error handling
- Invalid non-numeric values converted to NaN

### 9.4 Text Standardization
- Names: Strip whitespace, remove special characters, title case
- Departments: Canonical mapping (e.g., "cse", "C.S.E", "Computer Science" → "CSE")
- Emails: Lowercase, strip whitespace
- Courses: Title case normalization

### 9.5 Regex Validation
- Student ID: `^S\d{3}$` pattern
- Email: Standard RFC-like pattern
- Names: Letters, spaces, hyphens, apostrophes only
- Validation report with valid/invalid counts

### 9.6 Fuzzy Matching
- RapidFuzz token_sort_ratio for name comparison
- Configurable similarity threshold (default 85%)
- Standardization map generation for review

### 9.7 Outlier Detection
- IQR method: Q1 - 1.5×IQR to Q3 + 1.5×IQR
- Domain rules: Marks 0-100, Attendance 0-100, CGPA 0-10, etc.
- Invalid values → converted to NaN
- Valid extreme values → retained and flagged

## 10. Visualization Methodology

### Static (Matplotlib)
1. Marks Distribution Histogram
2. CGPA Distribution Histogram
3. Department-wise Average Marks Bar Chart
4. Course-wise Average Marks Bar Chart
5. Attendance vs Marks Scatter Plot
6. Semester-wise Performance Line Chart
7. Department-wise Attendance Bar Chart
8. Placement Status Bar/Pie Chart

### Interactive (Plotly via Streamlit)
1. Interactive Marks Distribution with hover data
2. Interactive Department Comparison
3. Interactive Attendance vs Marks Scatter
4. Interactive Semester Trend

### Filters
- Department, Course, Semester, Placement Status

## 11. Academic Insights

- **Students Requiring Support**: Based on CGPA < 6.0, Marks < 50, Attendance < 75%
- **Low-Performing Courses**: Courses below configurable threshold with recommendations
- **Attendance-Performance Correlation**: With interpretation (correlation ≠ causation)
- **Department Comparison**: Multi-metric departmental analysis
- **Placement Analysis**: Department-wise placement rates, performance comparison

## 12. Expected Output

- A professional Streamlit dashboard with 12 navigation sections
- 8 static charts saved to output/charts/
- Downloadable CSV reports (cleaned data, outlier report, fuzzy matching report, quality report)
- Comprehensive academic insights with configurable thresholds
- No placeholder or fake results — all calculations from actual data

## 13. Running Tests

Generate sample data and verify:
```bash
python generate_data.py
streamlit run app.py
```

Load sample data via sidebar, then navigate through each page to verify functionality.

---

**Note**: This project is designed for educational/academic demonstration purposes. The sample data contains intentionally introduced quality issues to demonstrate the system's data wrangling capabilities.
