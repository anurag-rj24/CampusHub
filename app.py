import os
import sys
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from database.connection import create_connection
from utils.password import verify_password, hash_password
from services.audit_service import AuditService

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "campushub_enterprise_secret_2026_x89q")

# Context manager for DB connections
def get_db():
    conn = create_connection()
    return conn

# Helper: Log audit action
def log_audit(user_id, action, table_name, record_id, description):
    try:
        AuditService.log_action(user_id, action, table_name, record_id, description)
    except Exception as e:
        print(f"Audit Log Error: {e}")

# Context processor for template globals
@app.context_processor
def inject_global_data():
    user = session.get('user')
    return {
        'current_user': user,
        'now': datetime.datetime.now()
    }

# Authentication Decorator with Strict Role Enforcement
def login_required(roles=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                flash("Please log in to access this portal.", "danger")
                return redirect(url_for('select_role'))
            if roles and session['user']['role'] not in roles:
                flash(f"Access Denied: You do not have permissions for the {session['user']['role']} portal.", "danger")
                role_dashboards = {
                    'STUDENT': 'student_dashboard',
                    'FACULTY': 'faculty_dashboard',
                    'ADMIN': 'admin_dashboard',
                    'SUPER_HEAD': 'super_head_dashboard'
                }
                return redirect(url_for(role_dashboards.get(session['user']['role'], 'select_role')))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


# ----------------------------------------------------
# AUTHENTICATION & GATEWAY ROUTES
# ----------------------------------------------------

@app.route('/')
def index():
    if 'user' in session:
        role = session['user']['role']
        if role == 'STUDENT':
            return redirect(url_for('student_dashboard'))
        elif role == 'FACULTY':
            return redirect(url_for('faculty_dashboard'))
        elif role == 'ADMIN':
            return redirect(url_for('admin_dashboard'))
        elif role == 'SUPER_HEAD':
            return redirect(url_for('super_head_dashboard'))
    return render_template('portal_select.html')


@app.route('/select-role')
def select_role():
    return render_template('portal_select.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    selected_role = request.args.get('role', '').upper()
    if not selected_role and request.method == 'POST':
        selected_role = request.form.get('role', '').upper()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', selected_role=selected_role)

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, first_name, middle_name, last_name, email, phone, password_hash, role, status, created_at, last_login
            FROM users
            WHERE email = %s AND status = 'ACTIVE'
        """, (email,))
        user_data = cursor.fetchone()

        if not user_data or not verify_password(password, user_data["password_hash"]):
            cursor.close()
            conn.close()
            flash("Invalid email or password, or account is inactive.", "danger")
            return render_template('login.html', selected_role=selected_role)

        # Strict Role Matching: If user selected a specific portal (e.g. Student), they must match that role
        if selected_role and user_data['role'] != selected_role:
            cursor.close()
            conn.close()
            role_name_map = {
                'STUDENT': 'Student',
                'FACULTY': 'Faculty',
                'ADMIN': 'Administrator',
                'SUPER_HEAD': 'Super Head'
            }
            actual_role_title = role_name_map.get(user_data['role'], user_data['role'])
            flash(f"Access Denied: This account is registered as '{actual_role_title}'. Please log in through the {actual_role_title} portal.", "danger")
            return render_template('login.html', selected_role=selected_role)

        # Update last login timestamp
        cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = %s", (user_data["user_id"],))
        conn.commit()
        cursor.close()
        conn.close()

        full_name = " ".join([p for p in [user_data["first_name"], user_data["middle_name"], user_data["last_name"]] if p])

        session['user'] = {
            'user_id': user_data['user_id'],
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'full_name': full_name,
            'email': user_data['email'],
            'phone': user_data['phone'],
            'role': user_data['role']
        }

        log_audit(user_data['user_id'], 'LOGIN', 'users', user_data['user_id'], f"User logged in as {user_data['role']}")
        flash(f"Welcome back, {full_name}!", "success")

        # Route strictly to the user's specific dashboard
        if user_data['role'] == 'STUDENT':
            return redirect(url_for('student_dashboard'))
        elif user_data['role'] == 'FACULTY':
            return redirect(url_for('faculty_dashboard'))
        elif user_data['role'] == 'ADMIN':
            return redirect(url_for('admin_dashboard'))
        elif user_data['role'] == 'SUPER_HEAD':
            return redirect(url_for('super_head_dashboard'))

    return render_template('login.html', selected_role=selected_role)


@app.route('/logout')
def logout():
    if 'user' in session:
        log_audit(session['user']['user_id'], 'LOGOUT', 'users', session['user']['user_id'], "User logged out")
        session.clear()
        flash("You have been logged out securely.", "info")
    return redirect(url_for('select_role'))


# ----------------------------------------------------
# STUDENT PORTAL ROUTES
# ----------------------------------------------------

@app.route('/student')
@app.route('/student/dashboard')
@login_required(['STUDENT'])
def student_dashboard():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Student Info
    cursor.execute("""
        SELECT s.student_id, s.admission_date, s.student_status, d.department_name, d.department_code
        FROM student s
        JOIN department d ON s.department_id = d.department_id
        WHERE s.user_id = %s
    """, (user_id,))
    student = cursor.fetchone() or {}
    student_id = student.get('student_id', 0)

    # Attendance Stats
    cursor.execute("""
        SELECT COUNT(a.attendance_id) AS total_sessions,
               SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS present_count
        FROM attendance a
        WHERE a.student_id = %s
    """, (student_id,))
    att_stat = cursor.fetchone() or {'total_sessions': 0, 'present_count': 0}
    total_sess = att_stat['total_sessions'] or 0
    pres_count = att_stat['present_count'] or 0
    att_pct = (pres_count / total_sess * 100) if total_sess > 0 else 0.0

    # Marks Stats
    cursor.execute("""
        SELECT AVG(m.total_marks) AS avg_score,
               COUNT(m.marks_id) AS total_assessments
        FROM marks m
        WHERE m.student_id = %s
    """, (student_id,))
    marks_stat = cursor.fetchone() or {'avg_score': 0, 'total_assessments': 0}
    avg_score = marks_stat['avg_score'] or 0.0

    # Open Placement Drives count
    cursor.execute("SELECT COUNT(*) AS total_drives FROM drive WHERE drive_status IN ('OPEN', 'UPCOMING')")
    open_drives = cursor.fetchone()['total_drives']

    # Pending Leaves
    cursor.execute("SELECT COUNT(*) AS pending_leaves FROM leave_request WHERE user_id = %s AND curr_status IN ('INITIAL_STAGE', 'PROCESSING')", (user_id,))
    pending_leaves = cursor.fetchone()['pending_leaves']

    # Recent Notices
    cursor.execute("""
        SELECT notice_id, title, content, target_role, created_at
        FROM notice
        WHERE target_role IN ('ALL', 'STUDENT')
        ORDER BY created_at DESC
        LIMIT 4
    """)
    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/dashboard.html',
                           student=student,
                           att_pct=round(att_pct, 1),
                           total_sess=total_sess,
                           pres_count=pres_count,
                           avg_score=round(avg_score, 1),
                           open_drives=open_drives,
                           pending_leaves=pending_leaves,
                           notices=notices)


@app.route('/student/profile')
@login_required(['STUDENT'])
def student_profile():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.phone, u.role, u.status, u.created_at, u.last_login,
               s.student_id, s.date_of_birth, s.gender, s.blood_group, s.father_name, s.mother_name,
               s.previous_qualification, s.previous_percentage, s.admission_date, s.address,
               s.city, s.state, s.pincode, s.emergency_contact, s.student_status,
               d.department_name, d.department_code
        FROM users u
        INNER JOIN student s ON u.user_id = s.user_id
        INNER JOIN department d ON s.department_id = d.department_id
        WHERE u.user_id = %s
    """, (user_id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('student/profile.html', profile=profile)


@app.route('/student/attendance')
@login_required(['STUDENT'])
def student_attendance():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    records = []
    overall_total = 0
    overall_present = 0

    if student:
        cursor.execute("""
            SELECT sub.subject_code, sub.subject_name, sub.credits,
                   COUNT(a.attendance_id) AS total_sessions,
                   SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS present_count,
                   SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END) AS absent_count
            FROM attendance a
            JOIN class_session cs ON a.session_id = cs.session_id
            JOIN subject sub ON cs.subject_id = sub.subject_id
            WHERE a.student_id = %s
            GROUP BY sub.subject_id, sub.subject_code, sub.subject_name, sub.credits
        """, (student['student_id'],))
        records = cursor.fetchall()

        for rec in records:
            tot = rec['total_sessions'] or 0
            prs = rec['present_count'] or 0
            rec['percentage'] = round((prs / tot * 100), 1) if tot > 0 else 100.0
            overall_total += tot
            overall_present += prs

    cursor.close()
    conn.close()

    overall_pct = round((overall_present / overall_total * 100), 1) if overall_total > 0 else 0.0
    return render_template('student/attendance.html', records=records, overall_total=overall_total, overall_present=overall_present, overall_pct=overall_pct)


@app.route('/student/academics')
@login_required(['STUDENT'])
def student_academics():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    enrollments = []
    marks_list = []

    if student:
        cursor.execute("""
            SELECT c.course_code, c.course_name, c.duration_years, c.degree_level,
                   se.enrollment_date, se.semester AS current_semester, se.status, d.department_name
            FROM student_enrollment se
            JOIN course c ON se.course_id = c.course_id
            JOIN department d ON c.department_id = d.department_id
            WHERE se.student_id = %s
        """, (student['student_id'],))
        enrollments = cursor.fetchall()

        cursor.execute("""
            SELECT sub.subject_code, sub.subject_name, sub.credits,
                   m.cca1, m.cca2, m.cca3, m.midterm, m.final_exam, m.total_marks, m.academic_year, m.semester
            FROM marks m
            JOIN subject sub ON m.subject_id = sub.subject_id
            WHERE m.student_id = %s
            ORDER BY sub.subject_code
        """, (student['student_id'],))
        marks_list = cursor.fetchall()

        for m in marks_list:
            tot = m['total_marks'] or (m['midterm'] or 0) + (m['final_exam'] or 0)
            m['marks_obtained'] = tot
            m['max_marks'] = 100
            m['exam_type'] = f"Sem {m['semester']} ({m['academic_year'] or '2025-26'})"
            if tot >= 90:
                m['grade'] = 'A+'
            elif tot >= 80:
                m['grade'] = 'A'
            elif tot >= 70:
                m['grade'] = 'B'
            elif tot >= 60:
                m['grade'] = 'C'
            elif tot >= 50:
                m['grade'] = 'D'
            else:
                m['grade'] = 'F'
            m['evaluation_date'] = 'Current Session'

    cursor.close()
    conn.close()
    return render_template('student/academics.html', enrollments=enrollments, marks=marks_list)


@app.route('/student/placements')
@login_required(['STUDENT'])
def student_placements():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    drives = []
    applications = []

    if student:
        cursor.execute("""
            SELECT d.drive_id, d.drive_title AS job_title, d.role_description AS job_description,
                   d.package_in_lpa AS package_lpa, d.job_location,
                   CONCAT('Min CGPA: ', d.minimum_cgpa, ', Branch: ', d.eligible_branch) AS eligibility_criteria,
                   d.drive_date, d.application_deadline, d.drive_status AS status,
                   c.company_name, c.industry_type AS industry, c.website,
                   (SELECT COUNT(*) FROM student_application sa WHERE sa.drive_id = d.drive_id AND sa.student_id = %s) AS has_applied
            FROM drive d
            JOIN company c ON d.company_id = c.company_id
            ORDER BY d.drive_date ASC
        """, (student['student_id'],))
        drives = cursor.fetchall()

        cursor.execute("""
            SELECT sa.application_id, sa.applied_at AS applied_date, sa.status, sa.remarks AS interview_feedback,
                   d.drive_title AS job_title, d.package_in_lpa AS package_lpa, c.company_name
            FROM student_application sa
            JOIN drive d ON sa.drive_id = d.drive_id
            JOIN company c ON d.company_id = c.company_id
            WHERE sa.student_id = %s
            ORDER BY sa.applied_at DESC
        """, (student['student_id'],))
        applications = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('student/placements.html', drives=drives, applications=applications)


@app.route('/student/apply-drive/<int:drive_id>', methods=['POST'])
@login_required(['STUDENT'])
def apply_drive(drive_id):
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for('student_placements'))

    cursor.execute("SELECT * FROM student_application WHERE student_id = %s AND drive_id = %s", (student['student_id'], drive_id))
    if cursor.fetchone():
        flash("You have already applied for this placement drive.", "warning")
    else:
        cursor.execute("INSERT INTO student_application (student_id, drive_id, status) VALUES (%s, %s, 'APPLIED')", (student['student_id'], drive_id))
        conn.commit()
        log_audit(user_id, 'INSERT', 'student_application', drive_id, f"Student applied for drive ID {drive_id}")
        flash("Placement application submitted successfully!", "success")

    cursor.close()
    conn.close()
    return redirect(url_for('student_placements'))


@app.route('/student/leaves', methods=['GET', 'POST'])
@login_required(['STUDENT'])
def student_leaves():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        leave_type = request.form.get('leave_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        reason = request.form.get('reason')

        if not leave_type or not start_date or not end_date or not reason:
            flash("All fields are required to submit a leave request.", "danger")
        else:
            cursor.execute("""
                INSERT INTO leave_request (user_id, leave_type, from_date, to_date, reason, curr_status)
                VALUES (%s, %s, %s, %s, %s, 'INITIAL_STAGE')
            """, (user_id, leave_type, start_date, end_date, reason))
            conn.commit()
            new_id = cursor.lastrowid
            log_audit(user_id, 'INSERT', 'leave_request', new_id, f"Submitted leave request {leave_type}")
            flash("Leave request submitted successfully for review.", "success")
            return redirect(url_for('student_leaves'))

    cursor.execute("""
        SELECT request_id AS leave_id, leave_type, from_date AS start_date, to_date AS end_date,
               reason, curr_status AS status, reviewer_comment AS action_remarks, reviewed_at AS action_date, applied_at AS created_at
        FROM leave_request
        WHERE user_id = %s
        ORDER BY applied_at DESC
    """, (user_id,))
    leaves = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('student/leaves.html', leaves=leaves)


# ----------------------------------------------------
# FACULTY PORTAL ROUTES
# ----------------------------------------------------

@app.route('/faculty')
@app.route('/faculty/dashboard')
@login_required(['FACULTY'])
def faculty_dashboard():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.faculty_id, f.designation, f.employment_type, d.department_name, d.department_code
        FROM faculty f
        LEFT JOIN department d ON f.department_id = d.department_id
        WHERE f.user_id = %s
    """, (user_id,))
    faculty = cursor.fetchone() or {}
    faculty_id = faculty.get('faculty_id', 0)

    # Assigned Subjects
    cursor.execute("""
        SELECT s.subject_id, s.subject_code, s.subject_name, s.credits, s.semester
        FROM faculty_subject fs
        JOIN subject s ON fs.subject_id = s.subject_id
        WHERE fs.faculty_id = %s
    """, (faculty_id,))
    assigned_subjects = cursor.fetchall()

    # Total Sessions Conducted
    cursor.execute("SELECT COUNT(*) AS total_sessions FROM class_session WHERE faculty_id = %s", (faculty_id,))
    total_sessions = cursor.fetchone()['total_sessions']

    # Pending student leaves
    cursor.execute("SELECT COUNT(*) AS pending_leaves FROM leave_request WHERE curr_status IN ('INITIAL_STAGE', 'PROCESSING')")
    pending_leaves = cursor.fetchone()['pending_leaves']

    # Campus notices
    cursor.execute("SELECT notice_id, title, content, created_at FROM notice WHERE target_role IN ('ALL', 'FACULTY') ORDER BY created_at DESC LIMIT 3")
    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('faculty/dashboard.html',
                           faculty=faculty,
                           assigned_subjects=assigned_subjects,
                           total_sessions=total_sessions,
                           pending_leaves=pending_leaves,
                           notices=notices)


@app.route('/faculty/profile')
@login_required(['FACULTY'])
def faculty_profile():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.phone, u.role, u.status, u.created_at, u.last_login,
               f.faculty_id, f.department_id, f.designation, f.date_of_birth, f.gender, f.blood_group,
               f.father_name, f.mother_name, f.address, f.city, f.state, f.pincode, f.qualification,
               f.specialization, f.joining_date, f.salary, f.employment_type, f.emergency_contact,
               d.department_name, d.department_code
        FROM users u
        INNER JOIN faculty f ON u.user_id = f.user_id
        LEFT JOIN department d ON f.department_id = d.department_id
        WHERE u.user_id = %s
    """, (user_id,))
    profile = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('faculty/profile.html', profile=profile)


@app.route('/faculty/attendance', methods=['GET', 'POST'])
@login_required(['FACULTY'])
def faculty_attendance():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (user_id,))
    faculty = cursor.fetchone()
    faculty_id = faculty['faculty_id'] if faculty else 0

    cursor.execute("""
        SELECT s.subject_id, s.subject_code, s.subject_name
        FROM faculty_subject fs
        JOIN subject s ON fs.subject_id = s.subject_id
        WHERE fs.faculty_id = %s
    """, (faculty_id,))
    subjects = cursor.fetchall()

    selected_subject_id = request.args.get('subject_id') or (subjects[0]['subject_id'] if subjects else None)
    students = []
    recent_sessions = []

    if selected_subject_id:
        cursor.execute("""
            SELECT s.student_id, u.first_name, u.last_name, u.email, d.department_code
            FROM student s
            JOIN users u ON s.user_id = u.user_id
            JOIN subject sub ON s.department_id = sub.department_id
            JOIN department d ON s.department_id = d.department_id
            WHERE sub.subject_id = %s AND s.student_status = 'ACTIVE'
            ORDER BY s.student_id
        """, (selected_subject_id,))
        students = cursor.fetchall()

        cursor.execute("""
            SELECT session_id, session_date, start_time, end_time, room_no, session_type
            FROM class_session
            WHERE subject_id = %s AND faculty_id = %s
            ORDER BY session_date DESC
            LIMIT 5
        """, (selected_subject_id, faculty_id))
        recent_sessions = cursor.fetchall()

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        session_date = request.form.get('session_date')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        room_no = request.form.get('room_no', 'Room 101')
        session_type = request.form.get('session_type', 'LECTURE')

        if not subject_id or not session_date or not start_time or not end_time:
            flash("All session details are required.", "danger")
        else:
            cursor.execute("""
                INSERT INTO class_session (subject_id, faculty_id, session_date, start_time, end_time, room_no, session_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (subject_id, faculty_id, session_date, start_time, end_time, room_no, session_type))
            session_id = cursor.lastrowid

            for st in students:
                st_id = st['student_id']
                status = request.form.get(f"status_{st_id}", "PRESENT")
                remarks = request.form.get(f"remarks_{st_id}", None)
                cursor.execute("""
                    INSERT INTO attendance (student_id, session_id, status, remarks)
                    VALUES (%s, %s, %s, %s)
                """, (st_id, session_id, status, remarks))

            conn.commit()
            log_audit(user_id, 'INSERT', 'class_session', session_id, f"Marked attendance for session ID {session_id}")
            flash(f"Class session recorded & attendance saved for {len(students)} students!", "success")
            return redirect(url_for('faculty_attendance', subject_id=subject_id))

    cursor.close()
    conn.close()

    return render_template('faculty/attendance.html',
                           subjects=subjects,
                           selected_subject_id=int(selected_subject_id) if selected_subject_id else None,
                           students=students,
                           recent_sessions=recent_sessions)


@app.route('/faculty/grading', methods=['GET', 'POST'])
@login_required(['FACULTY'])
def faculty_grading():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (user_id,))
    faculty = cursor.fetchone()
    faculty_id = faculty['faculty_id'] if faculty else 0

    cursor.execute("""
        SELECT s.subject_id, s.subject_code, s.subject_name
        FROM faculty_subject fs
        JOIN subject s ON fs.subject_id = s.subject_id
        WHERE fs.faculty_id = %s
    """, (faculty_id,))
    subjects = cursor.fetchall()

    selected_subject_id = request.args.get('subject_id') or (subjects[0]['subject_id'] if subjects else None)
    students = []
    existing_marks = {}

    if selected_subject_id:
        cursor.execute("""
            SELECT s.student_id, u.first_name, u.last_name, u.email
            FROM student s
            JOIN users u ON s.user_id = u.user_id
            JOIN subject sub ON s.department_id = sub.department_id
            WHERE sub.subject_id = %s AND s.student_status = 'ACTIVE'
            ORDER BY s.student_id
        """, (selected_subject_id,))
        students = cursor.fetchall()

        cursor.execute("""
            SELECT student_id, total_marks, midterm, final_exam
            FROM marks
            WHERE subject_id = %s
        """, (selected_subject_id,))
        marks_rows = cursor.fetchall()
        for r in marks_rows:
            existing_marks[f"{r['student_id']}_INTERNAL"] = {
                'marks_obtained': r['total_marks'] or (r['midterm'] or 0) + (r['final_exam'] or 0),
                'grade': 'A' if (r['total_marks'] or 0) >= 80 else 'B'
            }

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        max_marks = float(request.form.get('max_marks', 100))

        for st in students:
            st_id = st['student_id']
            marks_val = request.form.get(f"marks_{st_id}")
            if marks_val is not None and marks_val != "":
                obtained = int(float(marks_val))
                midterm_val = int(obtained * 0.4)
                final_val = int(obtained * 0.6)

                cursor.execute("""
                    INSERT INTO marks (student_id, subject_id, faculty_id, midterm, final_exam, total_marks, academic_year, semester)
                    VALUES (%s, %s, %s, %s, %s, %s, '2025-26', 1)
                    ON DUPLICATE KEY UPDATE midterm = VALUES(midterm), final_exam = VALUES(final_exam), total_marks = VALUES(total_marks)
                """, (st_id, subject_id, faculty_id, midterm_val, final_val, obtained))

        conn.commit()
        log_audit(user_id, 'UPDATE', 'marks', subject_id, f"Uploaded marks for subject ID {subject_id}")
        flash("Marks and evaluation updated successfully!", "success")
        return redirect(url_for('faculty_grading', subject_id=subject_id))

    cursor.close()
    conn.close()

    return render_template('faculty/grading.html',
                           subjects=subjects,
                           selected_subject_id=int(selected_subject_id) if selected_subject_id else None,
                           students=students,
                           existing_marks=existing_marks)


@app.route('/faculty/leaves')
@login_required(['FACULTY'])
def faculty_leaves():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT lr.request_id AS leave_id, lr.leave_type, lr.from_date AS start_date, lr.to_date AS end_date,
               lr.reason, lr.curr_status AS status, lr.applied_at AS created_at,
               u.first_name, u.last_name, u.role, u.email
        FROM leave_request lr
        JOIN users u ON lr.user_id = u.user_id
        ORDER BY lr.applied_at DESC
    """)
    leaves = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('faculty/leaves.html', leaves=leaves)


@app.route('/faculty/review-leave/<int:leave_id>', methods=['POST'])
@login_required(['FACULTY', 'ADMIN'])
def review_leave(leave_id):
    user_id = session['user']['user_id']
    status = request.form.get('status')
    remarks = request.form.get('remarks', '')

    if status not in ['APPROVED', 'REJECTED']:
        flash("Invalid action.", "danger")
        return redirect(request.referrer or url_for('faculty_leaves'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        UPDATE leave_request
        SET curr_status = %s, reviewed_by = %s, reviewer_comment = %s, reviewed_at = CURRENT_TIMESTAMP
        WHERE request_id = %s
    """, (status, user_id, remarks, leave_id))
    conn.commit()
    log_audit(user_id, 'UPDATE', 'leave_request', leave_id, f"Set leave status to {status}")
    cursor.close()
    conn.close()

    flash(f"Leave request marked as {status}!", "success")
    return redirect(request.referrer or url_for('faculty_leaves'))


# ----------------------------------------------------
# ADMINISTRATOR PORTAL ROUTES
# ----------------------------------------------------

@app.route('/admin')
@app.route('/admin/dashboard')
@login_required(['ADMIN'])
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_students FROM student WHERE student_status = 'ACTIVE'")
    total_students = cursor.fetchone()['total_students']

    cursor.execute("SELECT COUNT(*) AS total_faculty FROM faculty WHERE status = 'ACTIVE'")
    total_faculty = cursor.fetchone()['total_faculty']

    cursor.execute("SELECT COUNT(*) AS total_departments FROM department")
    total_departments = cursor.fetchone()['total_departments']

    cursor.execute("SELECT COUNT(*) AS total_courses FROM course")
    total_courses = cursor.fetchone()['total_courses']

    cursor.execute("SELECT COUNT(*) AS total_drives FROM drive WHERE drive_status IN ('OPEN', 'UPCOMING')")
    open_drives = cursor.fetchone()['total_drives']

    cursor.execute("""
        SELECT user_id, first_name, last_name, email, role, status, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 6
    """)
    recent_users = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/dashboard.html',
                           total_students=total_students,
                           total_faculty=total_faculty,
                           total_departments=total_departments,
                           total_courses=total_courses,
                           open_drives=open_drives,
                           recent_users=recent_users)


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required(['ADMIN'])
def admin_users():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        role = request.form.get('role')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password', 'test123')
        dept_id = request.form.get('department_id')

        if not first_name or not last_name or not email or not role or not dept_id:
            flash("All required fields must be filled.", "danger")
        else:
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email is already in use.", "danger")
            else:
                pw_hash = hash_password(password)
                cursor.execute("""
                    INSERT INTO users (first_name, last_name, email, phone, password_hash, role, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'ACTIVE')
                """, (first_name, last_name, email, phone, pw_hash, role))
                new_uid = cursor.lastrowid

                if role == 'STUDENT':
                    cursor.execute("""
                        INSERT INTO student (user_id, department_id, date_of_birth, gender, admission_date, address, student_status)
                        VALUES (%s, %s, '2002-01-01', 'MALE', CURRENT_DATE, 'Campus Hostel', 'ACTIVE')
                    """, (new_uid, dept_id))
                elif role == 'FACULTY':
                    cursor.execute("""
                        INSERT INTO faculty (user_id, department_id, designation, date_of_birth, gender, joining_date, salary, status)
                        VALUES (%s, %s, 'Assistant Professor', '1988-01-01', 'MALE', CURRENT_DATE, 65000.0, 'ACTIVE')
                    """, (new_uid, dept_id))

                conn.commit()
                log_audit(user_id, 'INSERT', 'users', new_uid, f"Admin created {role} account for {email}")
                flash(f"New {role} account created successfully!", "success")
                return redirect(url_for('admin_users'))

    cursor.execute("""
        SELECT u.user_id, u.first_name, u.last_name, u.email, u.phone, u.role, u.status, u.created_at, u.last_login,
               COALESCE(sd.department_name, fd.department_name, 'General') AS department_name
        FROM users u
        LEFT JOIN student s ON u.user_id = s.user_id
        LEFT JOIN department sd ON s.department_id = sd.department_id
        LEFT JOIN faculty f ON u.user_id = f.user_id
        LEFT JOIN department fd ON f.department_id = fd.department_id
        WHERE u.role IN ('STUDENT', 'FACULTY')
        ORDER BY u.created_at DESC
    """)
    users = cursor.fetchall()

    cursor.execute("SELECT department_id, department_name, department_code FROM department ORDER BY department_name")
    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/users.html', users=users, departments=departments)


@app.route('/admin/toggle-user-status/<int:uid>', methods=['POST'])
@login_required(['ADMIN', 'SUPER_HEAD'])
def toggle_user_status(uid):
    admin_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status, first_name, last_name, role FROM users WHERE user_id = %s", (uid,))
    target = cursor.fetchone()

    if target:
        new_status = 'INACTIVE' if target['status'] == 'ACTIVE' else 'ACTIVE'
        cursor.execute("UPDATE users SET status = %s WHERE user_id = %s", (new_status, uid))
        if target['role'] == 'STUDENT':
            cursor.execute("UPDATE student SET student_status = %s WHERE user_id = %s", (new_status, uid))
        elif target['role'] == 'FACULTY':
            cursor.execute("UPDATE faculty SET status = %s WHERE user_id = %s", (new_status, uid))
        elif target['role'] == 'ADMIN':
            cursor.execute("UPDATE admin SET status = %s WHERE user_id = %s", (new_status, uid))
        conn.commit()
        log_audit(admin_id, 'UPDATE', 'users', uid, f"Toggled user status to {new_status}")
        flash(f"User {target['first_name']} {target['last_name']} status updated to {new_status}.", "info")

    cursor.close()
    conn.close()
    return redirect(request.referrer or url_for('admin_users'))


@app.route('/admin/academics', methods=['GET', 'POST'])
@login_required(['ADMIN'])
def admin_academics():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        action_type = request.form.get('action_type')

        if action_type == 'add_course':
            course_name = request.form.get('course_name')
            course_code = request.form.get('course_code')
            dept_id = request.form.get('department_id')
            duration = request.form.get('duration_years', 4)
            degree_level = request.form.get('degree_level', 'UG')

            cursor.execute("""
                INSERT INTO course (course_name, course_code, department_id, duration_years, degree_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (course_name, course_code, dept_id, duration, degree_level))
            conn.commit()
            log_audit(user_id, 'INSERT', 'course', cursor.lastrowid, f"Added course {course_name}")
            flash(f"Course {course_name} added successfully!", "success")

        elif action_type == 'add_subject':
            subject_name = request.form.get('subject_name')
            subject_code = request.form.get('subject_code')
            dept_id = request.form.get('department_id')
            credits = request.form.get('credits', 4)
            semester = request.form.get('semester', 1)

            cursor.execute("""
                INSERT INTO subject (subject_name, subject_code, department_id, credits, semester, subject_type)
                VALUES (%s, %s, %s, %s, %s, 'THEORY')
            """, (subject_name, subject_code, dept_id, credits, semester))
            conn.commit()
            log_audit(user_id, 'INSERT', 'subject', cursor.lastrowid, f"Added subject {subject_name}")
            flash(f"Subject {subject_name} added successfully!", "success")

        return redirect(url_for('admin_academics'))

    cursor.execute("""
        SELECT c.course_id, c.course_name, c.course_code, c.duration_years, c.degree_level, d.department_name
        FROM course c
        JOIN department d ON c.department_id = d.department_id
        ORDER BY c.course_name
    """)
    courses = cursor.fetchall()

    cursor.execute("""
        SELECT s.subject_id, s.subject_name, s.subject_code, s.credits, s.semester, d.department_name
        FROM subject s
        JOIN department d ON s.department_id = d.department_id
        ORDER BY s.semester, s.subject_code
    """)
    subjects = cursor.fetchall()

    cursor.execute("SELECT department_id, department_name, department_code FROM department ORDER BY department_name")
    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/academics.html', courses=courses, subjects=subjects, departments=departments)


@app.route('/admin/placements', methods=['GET', 'POST'])
@login_required(['ADMIN'])
def admin_placements():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        company_name = request.form.get('company_name')
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        package_lpa = request.form.get('package_lpa', 0)
        job_location = request.form.get('job_location')
        eligibility = request.form.get('eligibility_criteria')
        drive_date = request.form.get('drive_date')
        deadline = request.form.get('application_deadline')

        cursor.execute("SELECT company_id FROM company WHERE company_name = %s", (company_name,))
        comp = cursor.fetchone()
        if not comp:
            cursor.execute("INSERT INTO company (company_name, industry_type) VALUES (%s, 'Technology')", (company_name,))
            company_id = cursor.lastrowid
        else:
            company_id = comp['company_id']

        cursor.execute("""
            INSERT INTO drive (company_id, drive_title, role_description, package_in_lpa, job_location, minimum_cgpa, eligible_branch, drive_date, application_deadline, drive_status, created_by)
            VALUES (%s, %s, %s, %s, %s, 6.5, %s, %s, %s, 'OPEN', %s)
        """, (company_id, job_title, job_description, package_lpa, job_location, eligibility, drive_date, deadline, user_id))
        conn.commit()
        log_audit(user_id, 'INSERT', 'drive', cursor.lastrowid, f"Created placement drive for {company_name}")
        flash(f"Placement drive for {company_name} created successfully!", "success")
        return redirect(url_for('admin_placements'))

    cursor.execute("""
        SELECT d.drive_id, d.drive_title AS job_title, d.package_in_lpa AS package_lpa, d.job_location,
               d.drive_date, d.application_deadline, d.drive_status AS status,
               c.company_name,
               (SELECT COUNT(*) FROM student_application sa WHERE sa.drive_id = d.drive_id) AS applicant_count
        FROM drive d
        JOIN company c ON d.company_id = c.company_id
        ORDER BY d.drive_date DESC
    """)
    drives = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/placements.html', drives=drives)


@app.route('/admin/notices', methods=['GET', 'POST'])
@login_required(['ADMIN', 'SUPER_HEAD'])
def admin_notices():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        target_role = request.form.get('target_role', 'ALL')

        if not title or not content:
            flash("Notice title and content are required.", "danger")
        else:
            cursor.execute("""
                INSERT INTO notice (title, content, target_role, release_date, is_active, created_by)
                VALUES (%s, %s, %s, CURRENT_DATE, 1, %s)
            """, (title, content, target_role, user_id))
            conn.commit()
            log_audit(user_id, 'INSERT', 'notice', cursor.lastrowid, f"Published notice: {title}")
            flash("Campus announcement published successfully!", "success")
            return redirect(url_for('admin_notices'))

    cursor.execute("""
        SELECT n.notice_id, n.title, n.content, n.target_role, 'NORMAL' AS priority, n.created_at,
               u.first_name, u.last_name
        FROM notice n
        JOIN users u ON n.created_by = u.user_id
        ORDER BY n.created_at DESC
    """)
    notices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/notices.html', notices=notices)


@app.route('/admin/reports')
@login_required(['ADMIN', 'SUPER_HEAD'])
def admin_reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.department_name, d.department_code,
               COUNT(DISTINCT s.student_id) AS student_count,
               COUNT(DISTINCT f.faculty_id) AS faculty_count
        FROM department d
        LEFT JOIN student s ON d.department_id = s.department_id AND s.student_status = 'ACTIVE'
        LEFT JOIN faculty f ON d.department_id = f.department_id AND f.status = 'ACTIVE'
        GROUP BY d.department_id, d.department_name, d.department_code
    """)
    dept_stats = cursor.fetchall()

    cursor.execute("""
        SELECT sub.subject_code, sub.subject_name,
               COUNT(a.attendance_id) AS total_marked,
               SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS present_total
        FROM subject sub
        LEFT JOIN class_session cs ON sub.subject_id = cs.subject_id
        LEFT JOIN attendance a ON cs.session_id = a.session_id
        GROUP BY sub.subject_id, sub.subject_code, sub.subject_name
    """)
    attendance_stats = cursor.fetchall()

    for item in attendance_stats:
        tot = item['total_marked'] or 0
        prs = item['present_total'] or 0
        item['pct'] = round((prs / tot * 100), 1) if tot > 0 else 0.0

    cursor.close()
    conn.close()

    return render_template('admin/reports.html', dept_stats=dept_stats, attendance_stats=attendance_stats)


# ----------------------------------------------------
# EXECUTIVE SUPER HEAD PORTAL ROUTES
# ----------------------------------------------------

@app.route('/super-head')
@app.route('/super-head/dashboard')
@login_required(['SUPER_HEAD'])
def super_head_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM users WHERE status = 'ACTIVE'")
    total_active_users = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM student WHERE student_status = 'ACTIVE'")
    total_students = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM faculty WHERE status = 'ACTIVE'")
    total_faculty = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM admin WHERE status = 'ACTIVE'")
    total_admins = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM department")
    total_depts = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM drive")
    total_drives = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM student_application WHERE status = 'SELECTED'")
    total_placed = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT d.department_name, d.department_code,
               COUNT(DISTINCT s.student_id) AS student_count,
               COUNT(DISTINCT f.faculty_id) AS faculty_count
        FROM department d
        LEFT JOIN student s ON d.department_id = s.department_id AND s.student_status = 'ACTIVE'
        LEFT JOIN faculty f ON d.department_id = f.department_id AND f.status = 'ACTIVE'
        GROUP BY d.department_id, d.department_name, d.department_code
        ORDER BY d.department_name
    """)
    dept_stats = cursor.fetchall()

    cursor.execute("""
        SELECT a.log_id, a.action, a.table_name, a.record_id, a.description, a.created_at AS timestamp,
               u.first_name, u.last_name, u.role
        FROM audit_log a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.created_at DESC
        LIMIT 6
    """)
    recent_logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('super_head/dashboard.html',
                           total_active_users=total_active_users,
                           total_students=total_students,
                           total_faculty=total_faculty,
                           total_admins=total_admins,
                           total_depts=total_depts,
                           total_drives=total_drives,
                           total_placed=total_placed,
                           dept_stats=dept_stats,
                           recent_logs=recent_logs)


@app.route('/super-head/departments', methods=['GET', 'POST'])
@login_required(['SUPER_HEAD'])
def super_head_departments():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        dept_name = request.form.get('department_name')
        dept_code = request.form.get('department_code', '').upper()

        if not dept_name or not dept_code:
            flash("Department name and code are required.", "danger")
        else:
            cursor.execute("SELECT department_id FROM department WHERE department_name = %s OR department_code = %s", (dept_name, dept_code))
            if cursor.fetchone():
                flash("Department name or code already exists.", "danger")
            else:
                cursor.execute("INSERT INTO department (department_name, department_code) VALUES (%s, %s)", (dept_name, dept_code))
                conn.commit()
                new_id = cursor.lastrowid
                log_audit(user_id, 'INSERT', 'department', new_id, f"Added department {dept_name} ({dept_code})")
                flash(f"Department {dept_name} ({dept_code}) added successfully!", "success")
                return redirect(url_for('super_head_departments'))

    cursor.execute("""
        SELECT d.department_id, d.department_name, d.department_code,
               (SELECT COUNT(*) FROM student s WHERE s.department_id = d.department_id) AS student_count,
               (SELECT COUNT(*) FROM faculty f WHERE f.department_id = d.department_id) AS faculty_count,
               (SELECT COUNT(*) FROM course c WHERE c.department_id = d.department_id) AS course_count
        FROM department d
        ORDER BY d.department_name
    """)
    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('super_head/departments.html', departments=departments)


@app.route('/super-head/admins', methods=['GET', 'POST'])
@login_required(['SUPER_HEAD'])
def super_head_admins():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password', 'test123')
        designation = request.form.get('designation', 'Academic Administrator')
        dept_id = request.form.get('department_id') or None

        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already registered in system.", "danger")
        else:
            pw_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, phone, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, 'ADMIN', 'ACTIVE')",
                (first_name, last_name, email, phone, pw_hash)
            )
            new_uid = cursor.lastrowid

            cursor.execute(
                """INSERT INTO admin (user_id, department_id, designation, date_of_birth, gender, qualification,
                                     joining_date, salary, address, status)
                   VALUES (%s, %s, %s, '1985-01-01', 'MALE', 'Master of Administration', CURRENT_DATE, 80000.0, 'Campus Admin Wing', 'ACTIVE')""",
                (new_uid, dept_id, designation)
            )
            conn.commit()
            log_audit(user_id, 'INSERT', 'admin', cursor.lastrowid, f"Created administrator {first_name} {last_name}")
            flash(f"Administrator {first_name} {last_name} created successfully!", "success")
            return redirect(url_for('super_head_admins'))

    cursor.execute("""
        SELECT a.admin_id, u.user_id, u.first_name, u.last_name, u.email, u.phone,
               a.designation, d.department_name, a.status, u.last_login
        FROM admin a
        JOIN users u ON a.user_id = u.user_id
        LEFT JOIN department d ON a.department_id = d.department_id
        ORDER BY a.admin_id
    """)
    admins = cursor.fetchall()

    cursor.execute("SELECT department_id, department_name FROM department ORDER BY department_name")
    departments = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('super_head/admins.html', admins=admins, departments=departments)


@app.route('/super-head/audit-logs')
@login_required(['SUPER_HEAD'])
def super_head_audit_logs():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.log_id, a.action, a.table_name, a.record_id, a.description, a.created_at AS timestamp,
               u.first_name, u.last_name, u.role, u.email
        FROM audit_log a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.created_at DESC
        LIMIT 100
    """)
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('super_head/audit_logs.html', logs=logs)


@app.route('/super-head/diagnostics')
@login_required(['SUPER_HEAD'])
def super_head_diagnostics():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    tables = ['users', 'student', 'faculty', 'admin', 'super_head', 'department', 'course', 'subject', 'class_session', 'attendance', 'marks', 'drive', 'student_application', 'leave_request', 'notice', 'audit_log']
    table_stats = []

    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) AS row_count FROM {t}")
            count = cursor.fetchone()['row_count']
            table_stats.append({'table': t, 'rows': count, 'status': 'HEALTHY'})
        except Exception as e:
            table_stats.append({'table': t, 'rows': 0, 'status': f'ERROR: {e}'})

    cursor.close()
    conn.close()

    return render_template('super_head/diagnostics.html', table_stats=table_stats)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("=====================================================")
    print(f"[*] CampusHub ERP Portal starting at http://localhost:{port}")
    print("=====================================================")
    app.run(host='0.0.0.0', port=port, debug=True)
