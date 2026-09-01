"""
Generate realistic sample datasets for the Student Academic Performance Data System.
Includes intentional data quality issues for testing.
"""
import csv
import json
import random
import os

random.seed(42)

FIRST_NAMES = [
    "Arun", "Priya", "Rahul", "Sneha", "Vikram", "Ananya", "Ravi", "Meera",
    "Sanjay", "Divya", "Karthik", "Neha", "Amit", "Pooja", "Suresh",
    "Kavita", "Rajesh", "Lakshmi", "Vijay", "Shreya", "Manish", "Pallavi",
    "Deepak", "Anjali", "Nitin", "Simran", "Prakash", "Ritu", "Sachin", "Nisha",
    "Aditya", "Tanvi", "Mohit", "Kavya", "Gaurav", "Megha", "Ashish", "Riya",
    "Rohan", "Pooja", "Raj", "Divya", "Sanjay", "Ananya", "Vikas", "Komal",
    "Nitin", "Sneha", "Aakash", "Mitali"
]

LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Reddy", "Nair", "Iyer", "Gupta", "Joshi",
    "Singh", "Verma", "Das", "Rao", "Mishra", "Choudhary", "Pandey",
    "Malhotra", "Kapoor", "Chauhan", "Mehta", "Sinha", "Bhatt", "Desai",
    "Thakur", "Tiwari", "Bhatt", "Rao", "Menon", "Pillai", "Mukherjee", "Sen"
]

DEPARTMENTS = ["CSE", "ECE", "EEE", "MECH", "CIVIL", "IT"]
DEPT_ALIASES = {
    "CSE": ["CSE", "cse", "C.S.E", "Computer Science", "CsE", "CS&E"],
    "ECE": ["ECE", "ece", "E.C.E", "Electronics", "EC"],
    "EEE": ["EEE", "eee", "E.E.E", "Electrical", "EE"],
    "MECH": ["MECH", "mech", "M.E.C.H", "Mechanical", "Mech"],
    "CIVIL": ["CIVIL", "civil", "C.I.V.I.L", "Civil", "Cvl"],
    "IT": ["IT", "it", "I.T", "Information Technology"],
}

COURSES_BY_DEPT = {
    "CSE": ["Data Structures", "Algorithms", "DBMS", "Operating Systems", "Computer Networks", "Machine Learning"],
    "ECE": ["Signals", "VLSI", "Digital Electronics", "Communication Systems", "Embedded Systems", "DSP"],
    "EEE": ["Power Systems", "Circuit Theory", "Control Systems", "Machines", "Power Electronics", "EMF"],
    "MECH": ["Thermodynamics", "Fluid Mechanics", "Machine Design", "CAD", "Manufacturing", "Heat Transfer"],
    "CIVIL": ["Structural Analysis", "Surveying", "Transportation", "Environmental", "Geotechnical", "Hydraulics"],
    "IT": ["Web Technologies", "Cloud Computing", "Cyber Security", "Software Engineering", "AI", "Data Mining"],
}

PLACEMENT_COMPANIES = [
    "TCS", "Infosys", "Wipro", "Google", "Microsoft", "Amazon", "Flipkart",
    "Accenture", "Cognizant", "HCL", "IBM", "Oracle", "SAP", "Capgemini",
    "L&T", "Samsung", "Reliance", "Tata Motors", "Bosch", "Qualcomm"
]


def random_student_id(i):
    return f"S{i:03d}"


def random_email(name, suffix):
    clean = name.lower().replace(" ", ".")
    domains = ["gmail.com", "yahoo.com", "college.edu", "hotmail.com"]
    return f"{clean}@{random.choice(domains)}"


def generate_admission(n=150):
    """Generate admission records with quality issues."""
    records = []
    used_ids = []

    for i in range(1, n + 1):
        sid = random_student_id(i)
        used_ids.append(sid)
        dept = random.choice(DEPARTMENTS)
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = random_email(first + " " + last, dept)
        gender = random.choice(["Male", "Female"])
        year = random.choice([2018, 2019, 2020, 2021, 2022])

        records.append({
            "Student_ID": sid,
            "Name": name,
            "Gender": gender,
            "Department": dept,
            "Email": email,
            "Admission_Year": year
        })

    # Add quality issues

    # Missing values
    for idx in [5, 12, 23, 34, 45, 56, 67, 78, 89, 100]:
        records[idx]["Name"] = ""
    for idx in [8, 18, 28, 38, 48]:
        records[idx]["Email"] = ""
    for idx in [3, 13, 33]:
        records[idx]["Department"] = ""
    for idx in [7, 17]:
        records[idx]["Gender"] = ""

    # Duplicate rows
    records.append(records[5].copy())
    records.append(records[20].copy())
    records.append(records[30].copy())

    # Duplicate Student_ID with different data
    records.append({
        "Student_ID": "S010",
        "Name": "Arun Kumr",
        "Gender": "Male",
        "Department": "cse",
        "Email": "arun.kumr@gmail.com",
        "Admission_Year": 2021
    })
    records.append({
        "Student_ID": "S025",
        "Name": "  PRIYA   SHARMA  ",
        "Gender": "Female",
        "Department": "C.S.E",
        "Email": "priya.sharma",
        "Admission_Year": 2020
    })

    # Names with extra spaces, wrong capitalization, typos
    records[10]["Name"] = "  ARUN   KUMAR  "
    records[15]["Name"] = "rahul sharma"
    records[20]["Name"] = "SNEHA  PATEL"
    records[25]["Name"] = "Vikram^Reddy"
    records[30]["Name"] = "ananya nair"
    records[35]["Name"] = "Ravi@Iyer"
    records[40]["Name"] = "  meera  gupta  "
    records[42]["Name"] = "Sanjay#Singh"
    records[44]["Name"] = "DIVYA VERMA"
    records[48]["Name"] = "Karthik  Das"
    records[50]["Name"] = "NEHA RAO"
    records[55]["Name"] = "amit mishra"
    records[60]["Name"] = "Pooja! Choudhary"
    records[65]["Name"] = "  Suresh  Pandey  "
    records[70]["Name"] = "Kavita&Malhotra"

    # Department variations
    records[14]["Department"] = "cse"
    records[16]["Department"] = "C.S.E"
    records[19]["Department"] = "Computer Science"
    records[22]["Department"] = "ece"
    records[26]["Department"] = "E.C.E"
    records[29]["Department"] = "Electronics"
    records[32]["Department"] = "eee"
    records[36]["Department"] = "E.E.E"
    records[39]["Department"] = "Electrical"
    records[41]["Department"] = "mech"
    records[43]["Department"] = "M.E.C.H"
    records[46]["Department"] = "civil"
    records[49]["Department"] = "C.I.V.I.L"
    records[52]["Department"] = "it"
    records[54]["Department"] = "I.T"

    # Invalid emails
    records[53]["Email"] = "invalid-email"
    records[57]["Email"] = "missing@at"
    records[61]["Email"] = "@nodomain.com"
    records[63]["Email"] = "spaces in@email.com"
    records[66]["Email"] = "no-domain"
    records[68]["Email"] = "missing_at_sign.com"

    return records


def generate_registration(admission_records, n=300):
    """Generate course registration records."""
    records = []
    student_ids = [r["Student_ID"] for r in admission_records if r["Student_ID"]]
    student_ids = list(set(student_ids))[:150]

    for i in range(n):
        sid = random.choice(student_ids)
        # Determine dept from admission
        dept_rec = next((r for r in admission_records if r["Student_ID"] == sid), None)
        dept = "CSE"
        if dept_rec:
            dept_raw = dept_rec["Department"].upper().replace(".", "").replace("&", "")
            for d in DEPARTMENTS:
                if d in dept_raw or dept_raw in d:
                    dept = d
                    break

        courses = COURSES_BY_DEPT.get(dept, COURSES_BY_DEPT["CSE"])
        course = random.choice(courses)
        credits = random.choice([3, 4, 4, 3, 2])
        semester = random.choice([1, 2, 3, 4, 5, 6, 7, 8])

        records.append({
            "Student_ID": sid,
            "Course": course,
            "Credits": credits,
            "Semester": semester
        })

    # Missing values
    for idx in [10, 25, 40, 55, 70]:
        records[idx]["Credits"] = ""
    for idx in [15, 30, 45]:
        records[idx]["Semester"] = ""

    # Invalid credits
    records[20]["Credits"] = -3
    records[35]["Credits"] = 0
    records[80]["Credits"] = "five"

    # Duplicate rows
    records.append(records[5].copy())
    records.append(records[15].copy())

    return records


def generate_attendance(admission_records, n=250):
    """Generate attendance records."""
    records = []
    student_ids = [r["Student_ID"] for r in admission_records if r["Student_ID"]]
    student_ids = list(set(student_ids))[:150]

    for i in range(n):
        sid = random.choice(student_ids)
        dept_rec = next((r for r in admission_records if r["Student_ID"] == sid), None)
        dept = "CSE"
        if dept_rec:
            dept_raw = dept_rec["Department"].upper().replace(".", "").replace("&", "")
            for d in DEPARTMENTS:
                if d in dept_raw or dept_raw in d:
                    dept = d
                    break
        courses = COURSES_BY_DEPT.get(dept, COURSES_BY_DEPT["CSE"])
        course = random.choice(courses)
        attendance = round(random.uniform(50, 100), 1)

        records.append({
            "Student_ID": sid,
            "Course": course,
            "Attendance": attendance
        })

    # Missing values
    for idx in [5, 20, 35, 50, 65, 80]:
        records[idx]["Attendance"] = ""

    # Invalid attendance
    records[18]["Attendance"] = 105.5
    records[28]["Attendance"] = -10
    records[48]["Attendance"] = 200
    records[60]["Attendance"] = "N/A"

    # Duplicate rows
    records.append(records[10].copy())

    return records


def generate_examination(admission_records, n=400):
    """Generate examination records with quality issues."""
    records = []
    student_ids = [r["Student_ID"] for r in admission_records if r["Student_ID"]]
    student_ids = list(set(student_ids))[:150]

    for i in range(n):
        sid = random.choice(student_ids)
        dept_rec = next((r for r in admission_records if r["Student_ID"] == sid), None)
        dept = "CSE"
        if dept_rec:
            dept_raw = dept_rec["Department"].upper().replace(".", "").replace("&", "")
            for d in DEPARTMENTS:
                if d in dept_raw or dept_raw in d:
                    dept = d
                    break
        courses = COURSES_BY_DEPT.get(dept, COURSES_BY_DEPT["CSE"])
        course = random.choice(courses)
        marks = round(random.uniform(20, 95), 1)
        semester = random.choice([1, 2, 3, 4, 5, 6, 7, 8])

        if marks >= 90:
            grade = "A+"
        elif marks >= 80:
            grade = "A"
        elif marks >= 70:
            grade = "B+"
        elif marks >= 60:
            grade = "B"
        elif marks >= 50:
            grade = "C"
        elif marks >= 40:
            grade = "D"
        else:
            grade = "F"

        records.append({
            "Student_ID": sid,
            "Course": course,
            "Marks": marks,
            "Grade": grade,
            "Semester": semester
        })

    # Missing values
    for idx in [10, 20, 30, 40, 50, 60, 70, 80]:
        records[idx]["Marks"] = ""
    for idx in [12, 22, 32]:
        records[idx]["Grade"] = ""

    # Invalid marks
    records[15]["Marks"] = 150
    records[25]["Marks"] = -20
    records[35]["Marks"] = 110
    records[45]["Marks"] = 105.5
    records[55]["Marks"] = "absent"
    records[65]["Marks"] = 999

    # Invalid semester
    records[75]["Semester"] = 0
    records[85]["Semester"] = -1
    records[95]["Semester"] = 10

    # Duplicate rows
    records.append(records[0].copy())
    records.append(records[25].copy())

    return records


def generate_placement(admission_records, n=100):
    """Generate placement records."""
    records = []
    student_ids = [r["Student_ID"] for r in admission_records if r["Student_ID"]]
    student_ids = list(set(student_ids))[:150]
    placed_ids = random.sample(student_ids, min(n, len(student_ids)))

    for sid in placed_ids:
        placed = random.random() < 0.65
        if placed:
            company = random.choice(PLACEMENT_COMPANIES)
            package = round(random.uniform(3.5, 45.0), 1)
        else:
            company = ""
            package = 0

        records.append({
            "Student_ID": sid,
            "Placement_Status": "Placed" if placed else "Not Placed",
            "Company": company,
            "Package_LPA": package
        })

    # Missing values
    for idx in [5, 10, 15]:
        records[idx]["Placement_Status"] = ""
    for idx in [8, 12]:
        records[idx]["Company"] = ""

    # Invalid package
    records[20]["Package_LPA"] = -5
    records[25]["Package_LPA"] = 1000
    records[30]["Package_LPA"] = "high"

    # Duplicate rows
    records.append(records[3].copy())

    return records


def save_csv(records, filename):
    if not records:
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)


def save_json(records, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def save_xml(records, filename):
    """Save records as XML."""
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<records>']
    for rec in records:
        lines.append("  <record>")
        for key, val in rec.items():
            lines.append(f"    <{key}>{val}</{key}>")
        lines.append("  </record>")
    lines.append("</records>")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("Generating admission records...")
    admission = generate_admission(150)
    save_csv(admission, os.path.join(data_dir, "admission.csv"))
    print(f"  -> admission.csv ({len(admission)} records)")

    print("Generating registration records...")
    registration = generate_registration(admission, 300)
    save_json(registration, os.path.join(data_dir, "registration.json"))
    print(f"  -> registration.json ({len(registration)} records)")

    print("Generating attendance records...")
    attendance = generate_attendance(admission, 250)
    save_xml(attendance, os.path.join(data_dir, "attendance.xml"))
    print(f"  -> attendance.xml ({len(attendance)} records)")

    print("Generating examination records...")
    examination = generate_examination(admission, 400)
    save_csv(examination, os.path.join(data_dir, "examination.csv"))
    print(f"  -> examination.csv ({len(examination)} records)")

    print("Generating placement records...")
    placement = generate_placement(admission, 100)
    save_json(placement, os.path.join(data_dir, "placement.json"))
    print(f"  -> placement.json ({len(placement)} records)")

    print("\nAll sample datasets generated successfully!")


if __name__ == "__main__":
    main()
