from flask import Flask, render_template, request
import sqlite3

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

app = Flask(__name__)

# Database connection
def get_db():
    return sqlite3.connect("students.db")


# Create tables without deleting existing data
def create_table():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            usn TEXT,
            email TEXT,
            department TEXT,
            semester INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT,
            subject TEXT,
            marks INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT,
            total_classes INTEGER,
            attended_classes INTEGER
        )
    """)

    conn.commit()
    conn.close()


create_table()
# AI MODEL TRAINING

training_data = pd.DataFrame({
    "marks": [
        25, 35, 40, 45, 50, 55,
        60, 65, 70, 75, 80, 85,
        90, 95, 30, 48, 68, 88
    ],
    "attendance": [
        40, 50, 55, 65, 60, 70,
        65, 75, 80, 70, 85, 90,
        95, 98, 45, 58, 72, 88
    ]
})

training_labels = [
    "Needs Improvement",
    "Needs Improvement",
    "Needs Improvement",
    "Needs Improvement",
    "Average Performance",
    "Average Performance",
    "Average Performance",
    "Average Performance",
    "Average Performance",
    "Good Performance",
    "Good Performance",
    "Good Performance",
    "Good Performance",
    "Good Performance",
    "Needs Improvement",
    "Needs Improvement",
    "Average Performance",
    "Good Performance"
]

ai_model = DecisionTreeClassifier(random_state=42)
ai_model.fit(training_data, training_labels)


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Register student
@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    usn = request.form["usn"]
    email = request.form["email"]
    department = request.form["department"]
    semester = request.form["semester"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE usn = ?", (usn,))
    existing = cursor.fetchone()

    if existing:
        conn.close()
        return "This USN is already registered."

    cursor.execute("""
        INSERT INTO students
        (name, usn, email, department, semester)
        VALUES (?, ?, ?, ?, ?)
    """, (name, usn, email, department, semester))

    conn.commit()
    conn.close()

    return "<h2>Student Registered Successfully!</h2><a href='/'>Go Back</a>"


# View all students
@app.route("/students")
def students():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students ORDER BY name")
    student_list = cursor.fetchall()

    conn.close()

    return render_template("students.html", students=student_list)


# Marks page
@app.route("/marks")
def marks_page():
    return render_template("marks.html")


# Add marks
@app.route("/add_marks", methods=["POST"])
def add_marks():
    usn = request.form["usn"]
    subject = request.form["subject"]
    marks = float(request.form["marks"])

    if marks < 0 or marks > 100:
        return "Marks must be between 0 and 100."

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE usn = ?", (usn,))
    if cursor.fetchone() is None:
        conn.close()
        return "Student USN not found. Please register first."

    cursor.execute("""
        INSERT INTO marks (usn, subject, marks)
        VALUES (?, ?, ?)
    """, (usn, subject, marks))

    conn.commit()
    conn.close()

    return "<h2>Marks Saved Successfully!</h2><a href='/marks'>Go Back</a>"


# View marks
@app.route("/view_marks")
def view_marks():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM marks")
    mark_list = cursor.fetchall()

    conn.close()

    return render_template("view_marks.html", marks=mark_list)


# Attendance page
@app.route("/attendance")
def attendance_page():
    return render_template("attendance.html")


# Add attendance
@app.route("/add_attendance", methods=["POST"])
def add_attendance():
    usn = request.form["usn"]
    total_classes = int(request.form["total_classes"])
    attended_classes = int(request.form["attended_classes"])

    if total_classes <= 0 or attended_classes < 0:
        return "Invalid attendance details."

    if attended_classes > total_classes:
        return "Attended classes cannot exceed total classes."

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE usn = ?", (usn,))
    if cursor.fetchone() is None:
        conn.close()
        return "Student USN not found. Please register first."

    cursor.execute("""
        INSERT INTO attendance
        (usn, total_classes, attended_classes)
        VALUES (?, ?, ?)
    """, (usn, total_classes, attended_classes))

    conn.commit()
    conn.close()

    return "<h2>Attendance Saved Successfully!</h2><a href='/attendance'>Go Back</a>"


# View attendance
@app.route("/view_attendance")
def view_attendance():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance")
    attendance_list = cursor.fetchall()

    conn.close()

    return render_template(
        "view_attendance.html",
        attendance=attendance_list
    )


# Performance page
@app.route("/performance", methods=["GET"])
def performance_page():
    return render_template("performance.html")


# Performance analysis
@app.route("/performance", methods=["POST"])
def performance():
    usn = request.form["usn"]
    marks = float(request.form["marks"])
    attendance = float(request.form["attendance"])

    if not (0 <= marks <= 100 and 0 <= attendance <= 100):
        return "Marks and attendance must be between 0 and 100."

    if marks >= 75 and attendance >= 75:
        result = "Good Performance"
    elif marks >= 50 and attendance >= 60:
        result = "Average Performance"
    else:
        result = "Needs Improvement"

    return f"""
        <h1>Performance Analysis</h1>
        <h2>USN: {usn}</h2>
        <h2>Marks: {marks}</h2>
        <h2>Attendance: {attendance}%</h2>
        <h2>Result: {result}</h2>
        <a href="/">Go Back</a>
    """
@app.route("/ai_prediction", methods=["GET", "POST"])
def ai_prediction():

    if request.method == "POST":
        usn = request.form["usn"]
        marks = float(request.form["marks"])
        attendance = float(request.form["attendance"])

        if not (0 <= marks <= 100 and 0 <= attendance <= 100):
            return "Marks and attendance must be between 0 and 100."

        input_data = pd.DataFrame(
            [[marks, attendance]],
            columns=["marks", "attendance"]
        )

        prediction = ai_model.predict(input_data)[0]

        return render_template(
            "prediction.html",
            prediction=prediction,
            usn=usn,
            marks=marks,
            attendance=attendance
        )

    return render_template("prediction.html")

@app.route("/dashboard")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM marks")
    total_marks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_marks=total_marks,
        total_attendance=total_attendance
    )
if __name__ == "__main__":
    app.run(debug=True)