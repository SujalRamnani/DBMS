from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import mysql.connector
from datetime import datetime, date
import os
from werkzeug.utils import secure_filename
import random

app = Flask(__name__)
app.secret_key = 'student_management_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="siddharth1712",  # Replace with your MySQL password
        database="student_management"
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper function to execute SQL queries
def execute_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        
        if commit:
            conn.commit()
            result = cursor.lastrowid
            
        return result
    except mysql.connector.Error as error:
        print(f"Database error: {error}")
        return None
    finally:
        cursor.close()
        conn.close()

# Routes
@app.route('/')
def home():
    # Get counts for dashboard
    student_count = execute_query("SELECT COUNT(*) as count FROM students", fetchone=True)
    subject_count = execute_query("SELECT COUNT(*) as count FROM subjects", fetchone=True)
    
    # Get recent students
    recent_students = execute_query(
        "SELECT * FROM students ORDER BY date_joined DESC LIMIT 5", 
        fetchall=True
    )
    
    return render_template(
        'index.html', 
        student_count=student_count['count'], 
        subject_count=subject_count['count'],
        recent_students=recent_students
    )

# Student Routes
@app.route('/students')
def view_students():
    students = execute_query("SELECT * FROM students ORDER BY name", fetchall=True)
    return render_template('students/view_students.html', students=students)

@app.route('/students/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        course = request.form['course']
        year = request.form['year']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        # Check if roll number already exists
        student = execute_query(
            "SELECT * FROM students WHERE roll_no = %s", 
            (roll_no,), 
            fetchone=True
        )
        
        if student:
            flash("Roll number already exists!", "error")
            return render_template('students/add_student.html')
        
        # Handle profile picture upload
        profile_pic = 'default.png'
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                new_filename = f"{roll_no}_{int(datetime.now().timestamp())}.{filename.rsplit('.', 1)[1].lower()}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                profile_pic = new_filename
        
        # Insert new student
        student_id = execute_query(
            """INSERT INTO students 
               (name, roll_no, course, year, email, phone, profile_pic, address) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, roll_no, course, year, email, phone, profile_pic, address),
            commit=True
        )
        
        flash("Student added successfully!", "success")
        return redirect(url_for('view_students'))
    
    return render_template('students/add_student.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        course = request.form['course']
        year = request.form['year']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        # Check if roll number already exists for a different student
        student = execute_query(
            "SELECT * FROM students WHERE roll_no = %s AND id != %s", 
            (roll_no, id), 
            fetchone=True
        )
        
        if student:
            flash("Roll number already assigned to another student!", "error")
            # Get current student data
            student = execute_query("SELECT * FROM students WHERE id = %s", (id,), fetchone=True)
            return render_template('students/edit_student.html', student=student)
        
        # Handle profile picture upload
        if 'profile_pic' in request.files and request.files['profile_pic'].filename != '':
            file = request.files['profile_pic']
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Generate unique filename
                new_filename = f"{roll_no}_{int(datetime.now().timestamp())}.{filename.rsplit('.', 1)[1].lower()}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                
                # Update profile picture name in database
                execute_query(
                    "UPDATE students SET profile_pic = %s WHERE id = %s",
                    (new_filename, id),
                    commit=True
                )
        
        # Update student information
        execute_query(
            """UPDATE students 
               SET name = %s, roll_no = %s, course = %s, year = %s, 
                   email = %s, phone = %s, address = %s 
               WHERE id = %s""",
            (name, roll_no, course, year, email, phone, address, id),
            commit=True
        )
        
        flash("Student updated successfully!", "success")
        return redirect(url_for('view_students'))
    
    # GET request - show form with current values
    student = execute_query("SELECT * FROM students WHERE id = %s", (id,), fetchone=True)
    
    if student:
        return render_template('students/edit_student.html', student=student)
    else:
        flash("Student not found!", "error")
        return redirect(url_for('view_students'))

@app.route('/students/profile/<int:id>')
def student_profile(id):
    student = execute_query("SELECT * FROM students WHERE id = %s", (id,), fetchone=True)
    
    if not student:
        flash("Student not found!", "error")
        return redirect(url_for('view_students'))
    
    # Get attendance records
    attendance = execute_query(
        "SELECT * FROM attendance WHERE student_id = %s ORDER BY date DESC LIMIT 10", 
        (id,), 
        fetchall=True
    )
    
    # Get marks records
    marks = execute_query(
        """SELECT m.*, s.name as subject_name 
           FROM marks m 
           JOIN subjects s ON m.subject_id = s.id 
           WHERE m.student_id = %s 
           ORDER BY m.exam_date DESC""", 
        (id,), 
        fetchall=True
    )
    
    # Get fee records
    fees = execute_query(
        "SELECT * FROM fees WHERE student_id = %s ORDER BY payment_date DESC", 
        (id,), 
        fetchall=True
    )
    
    # Calculate attendance statistics
    attendance_stats = {
        'total': len(attendance),
        'present': sum(1 for a in attendance if a['status'] == 'Present'),
        'absent': sum(1 for a in attendance if a['status'] == 'Absent'),
        'late': sum(1 for a in attendance if a['status'] == 'Late')
    }
    
    # Calculate academic performance
    performance = {}
    if marks:
        total_percentage = sum((m['marks'] / m['max_marks']) * 100 for m in marks) / len(marks)
        performance = {
            'total_exams': len(marks),
            'average_percentage': round(total_percentage, 2)
        }
    
    return render_template(
        'students/student_profile.html', 
        student=student,
        attendance=attendance,
        marks=marks,
        fees=fees,
        attendance_stats=attendance_stats,
        performance=performance
    )

@app.route('/students/delete/<int:id>', methods=['POST'])
def delete_student(id):
    execute_query("DELETE FROM students WHERE id = %s", (id,), commit=True)
    flash("Student deleted successfully!", "success")
    return redirect(url_for('view_students'))

# Attendance Routes
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        date_str = request.form['date']
        course = request.form['course']
        year = request.form['year']
        
        # Get students for the selected class
        students = execute_query(
            "SELECT * FROM students WHERE course = %s AND year = %s ORDER BY name",
            (course, year),
            fetchall=True
        )
        
        return render_template(
            'attendance/mark_attendance.html',
            students=students,
            date=date_str,
            course=course,
            year=year
        )
    
    return render_template('attendance/attendance.html')

@app.route('/attendance/save', methods=['POST'])
def save_attendance():
    date_str = request.form['date']
    student_ids = request.form.getlist('student_id')
    statuses = request.form.getlist('status')
    
    # Convert date string to date object
    attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Check if today's attendance has already been marked
    existing = execute_query(
        "SELECT student_id FROM attendance WHERE date = %s AND student_id IN ({})".format(
            ','.join(['%s'] * len(student_ids))
        ),
        (attendance_date, *student_ids),
        fetchall=True
    )
    
    existing_ids = [str(record['student_id']) for record in existing] if existing else []
    
    # Insert or update attendance records
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for i, student_id in enumerate(student_ids):
            if student_id in existing_ids:
                # Update existing record
                cursor.execute(
                    "UPDATE attendance SET status = %s WHERE student_id = %s AND date = %s",
                    (statuses[i], student_id, attendance_date)
                )
            else:
                # Insert new record
                cursor.execute(
                    "INSERT INTO attendance (student_id, date, status) VALUES (%s, %s, %s)",
                    (student_id, attendance_date, statuses[i])
                )
        
        conn.commit()
        flash("Attendance saved successfully!", "success")
    except mysql.connector.Error as error:
        print(f"Error saving attendance: {error}")
        flash("Error saving attendance. Please try again.", "error")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('view_attendance'))

@app.route('/attendance/view')
def view_attendance():
    # Get all attendance records grouped by date
    attendance = execute_query(
        """SELECT a.date, 
                  COUNT(*) as total_students,
                  SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present,
                  SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) as absent,
                  SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) as late
           FROM attendance a
           GROUP BY a.date
           ORDER BY a.date DESC""",
        fetchall=True
    )
    
    return render_template('attendance/view_attendance.html', attendance=attendance)

@app.route('/attendance/details/<date>')
def attendance_details(date):
    # Get attendance details for specific date
    details = execute_query(
        """SELECT a.*, s.name, s.roll_no, s.course, s.year, s.profile_pic 
           FROM attendance a
           JOIN students s ON a.student_id = s.id
           WHERE a.date = %s
           ORDER BY s.name""",
        (date,),
        fetchall=True
    )
    
    return render_template('attendance/attendance_details.html', details=details, date=date)

# Marks Routes
@app.route('/marks')
def marks():
    subjects = execute_query("SELECT * FROM subjects ORDER BY name", fetchall=True)
    return render_template('marks/marks.html', subjects=subjects)

@app.route('/marks/add', methods=['GET', 'POST'])
def add_marks():
    if request.method == 'POST':
        subject_id = request.form['subject_id']
        course = request.form['course']
        year = request.form['year']
        exam_type = request.form['exam_type']
        exam_date = request.form['exam_date']
        max_marks = request.form['max_marks']
        
        # Get students for the selected class
        students = execute_query(
            "SELECT * FROM students WHERE course = %s AND year = %s ORDER BY name",
            (course, year),
            fetchall=True
        )
        
        return render_template(
            'marks/add_marks_form.html',
            students=students,
            subject_id=subject_id,
            exam_type=exam_type,
            exam_date=exam_date,
            max_marks=max_marks
        )
    
    subjects = execute_query("SELECT * FROM subjects ORDER BY name", fetchall=True)
    return render_template('marks/add_marks.html', subjects=subjects)

@app.route('/marks/save', methods=['POST'])
def save_marks():
    subject_id = request.form['subject_id']
    exam_type = request.form['exam_type']
    exam_date = request.form['exam_date']
    max_marks = request.form['max_marks']
    student_ids = request.form.getlist('student_id')
    marks_list = request.form.getlist('marks')
    
    # Convert exam date string to date object
    exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
    
    # Insert marks records
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for i, student_id in enumerate(student_ids):
            # Check if marks already exist
            cursor.execute(
                """SELECT * FROM marks 
                   WHERE student_id = %s AND subject_id = %s AND exam_type = %s AND exam_date = %s""",
                (student_id, subject_id, exam_type, exam_date_obj)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing record
                cursor.execute(
                    """UPDATE marks 
                       SET marks = %s, max_marks = %s 
                       WHERE student_id = %s AND subject_id = %s AND exam_type = %s AND exam_date = %s""",
                    (marks_list[i], max_marks, student_id, subject_id, exam_type, exam_date_obj)
                )
            else:
                # Insert new record
                cursor.execute(
                    """INSERT INTO marks 
                       (student_id, subject_id, exam_type, marks, max_marks, exam_date) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (student_id, subject_id, exam_type, marks_list[i], max_marks, exam_date_obj)
                )
        
        conn.commit()
        flash("Marks saved successfully!", "success")
    except mysql.connector.Error as error:
        print(f"Error saving marks: {error}")
        flash("Error saving marks. Please try again.", "error")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('view_marks'))

@app.route('/marks/view')
def view_marks():
    # Get all exam records grouped by subject and date
    exams = execute_query(
        """SELECT m.subject_id, m.exam_type, m.exam_date, s.name as subject_name,
                  COUNT(*) as total_students,
                  AVG(m.marks) as avg_marks,
                  MAX(m.marks) as highest_mark,
                  MIN(m.marks) as lowest_mark,
                  m.max_marks
           FROM marks m
           JOIN subjects s ON m.subject_id = s.id
           GROUP BY m.subject_id, m.exam_type, m.exam_date
           ORDER BY m.exam_date DESC""",
        fetchall=True
    )
    
    return render_template('marks/view_marks.html', exams=exams)

@app.route('/marks/details/<int:subject_id>/<exam_type>/<exam_date>')
def marks_details(subject_id, exam_type, exam_date):
    # Get marks details for specific exam
    details = execute_query(
        """SELECT m.*, s.name, s.roll_no, s.course, s.year, s.profile_pic,
                  sub.name as subject_name
           FROM marks m
           JOIN students s ON m.student_id = s.id
           JOIN subjects s ON m.subject_id = s.id
           WHERE m.subject_id = %s AND m.exam_type = %s AND m.exam_date = %s
           ORDER BY s.name""",
        (subject_id, exam_type, exam_date),
        fetchall=True
    )
    
    subject_name = execute_query(
        "SELECT name FROM subjects WHERE id = %s",
        (subject_id,),
        fetchone=True
    )['name']
    
    return render_template(
        'marks/marks_details.html', 
        details=details, 
        subject_name=subject_name,
        exam_type=exam_type, 
        exam_date=exam_date
    )

# Fees Routes
@app.route('/fees')
def fees():
    students = execute_query("SELECT id, name, roll_no FROM students ORDER BY name", fetchall=True)
    return render_template('fees/fees.html', students=students)

@app.route('/fees/add', methods=['GET', 'POST'])
def add_fees():
    if request.method == 'POST':
        student_id = request.form['student_id']
        fee_type = request.form['fee_type']
        amount = request.form['amount']
        payment_date = request.form['payment_date']
        payment_method = request.form['payment_method']
        payment_status = request.form['payment_status']
        
        # Insert fee record
        execute_query(
            """INSERT INTO fees 
               (student_id, fee_type, amount, payment_date, payment_method, payment_status) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (student_id, fee_type, amount, payment_date, payment_method, payment_status),
            commit=True
        )
        
        flash("Fee record added successfully!", "success")
        return redirect(url_for('view_fees'))
    
    students = execute_query("SELECT id, name, roll_no FROM students ORDER BY name", fetchall=True)
    return render_template('fees/add_fees.html', students=students)

@app.route('/fees/view')
def view_fees():
    # Get all fee records with student details
    fees = execute_query(
        """SELECT f.*, s.name, s.roll_no, s.course, s.year
           FROM fees f
           JOIN students s ON f.student_id = s.id
           ORDER BY f.payment_date DESC""",
        fetchall=True
    )
    
    return render_template('fees/view_fees.html', fees=fees)

# API for charts on dashboard
@app.route('/api/attendance/stats')
def attendance_stats_api():
    # Get attendance statistics for the past 7 days
    stats = execute_query(
        """SELECT a.date, 
                  COUNT(*) as total,
                  SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) as present,
                  SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) as absent,
                  SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) as late
           FROM attendance a
           GROUP BY a.date
           ORDER BY a.date DESC
           LIMIT 7""",
        fetchall=True
    )
    
    # Format for chart
    dates = []
    present_data = []
    absent_data = []
    late_data = []
    
    for day in reversed(stats):
        dates.append(day['date'].strftime('%d-%m'))
        present_data.append(day['present'])
        absent_data.append(day['absent'])
        late_data.append(day['late'])
    
    return jsonify({
        'labels': dates,
        'datasets': [
            {
                'label': 'Present',
                'data': present_data,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Absent',
                'data': absent_data,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Late',
                'data': late_data,
                'backgroundColor': 'rgba(255, 206, 86, 0.2)',
                'borderColor': 'rgba(255, 206, 86, 1)',
                'borderWidth': 1
            }
        ]
    })

@app.route('/api/performance/course')
def course_performance_api():
    # Get average marks by course
    performance = execute_query(
        """SELECT s.course, AVG(m.marks / m.max_marks * 100) as avg_percentage
           FROM marks m
           JOIN students s ON m.student_id = s.id
           GROUP BY s.course""",
        fetchall=True
    )
    
    courses = []
    percentages = []
    
    for p in performance:
        courses.append(p['course'])
        percentages.append(round(p['avg_percentage'], 2))
    
    return jsonify({
        'labels': courses,
        'datasets': [{
            'label': 'Average Performance (%)',
            'data': percentages,
            'backgroundColor': [
                'rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)'
            ],
            'borderColor': [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)'
            ],
            'borderWidth': 1
        }]
    })

if __name__ == '__main__':
    app.run(debug=True)