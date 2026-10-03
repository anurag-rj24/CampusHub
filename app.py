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

    # Course Completion Progress (160 Total Degree Credits)
    cursor.execute("SELECT SUM(credits) AS total_earned_credits FROM mooc_course WHERE student_id = %s AND status = 'COMPLETED'", (student_id,))
    mooc_cr = cursor.fetchone()['total_earned_credits'] or 0
    earned_credits = 96 + mooc_cr  # Core + MOOC credits earned
    total_degree_credits = 160
    completion_pct = round((earned_credits / total_degree_credits) * 100, 1)

    # Fee Due Status
    cursor.execute("SELECT SUM(due_amount) AS total_due FROM student_fee WHERE student_id = %s", (student_id,))
    fee_stat = cursor.fetchone()
    total_due = fee_stat['total_due'] if fee_stat and fee_stat['total_due'] else 0.0

    # Open Placement Drives count
    cursor.execute("SELECT COUNT(*) AS total_drives FROM drive WHERE drive_status IN ('OPEN', 'UPCOMING')")
    open_drives = cursor.fetchone()['total_drives']

    # Pending Leaves
    cursor.execute("SELECT COUNT(*) AS pending_leaves FROM leave_request WHERE user_id = %s AND curr_status IN ('INITIAL_STAGE', 'PROCESSING')", (user_id,))
    pending_leaves = cursor.fetchone()['pending_leaves']

    # Today's Scheduled Classes
    cursor.execute("""
        SELECT ct.start_time, ct.end_time, ct.room_no, ct.session_type,
               sub.subject_code, sub.subject_name,
               u.first_name AS faculty_name
        FROM class_timetable ct
        JOIN subject sub ON ct.subject_id = sub.subject_id
        JOIN faculty f ON ct.faculty_id = f.faculty_id
        JOIN users u ON f.user_id = u.user_id
        WHERE ct.day_of_week = 'MONDAY'
        ORDER BY ct.start_time ASC
        LIMIT 3
    """)
    today_classes = cursor.fetchall()

    # Recent Notices
    cursor.execute("""
        SELECT notice_id, title, content, target_role, created_at
        FROM notice
        WHERE target_role IN ('ALL', 'STUDENT')
        ORDER BY created_at DESC
        LIMIT 3
    """)
    notices = cursor.fetchall()

    # Subject-wise attendance details matching MIT-WPU portal
    cursor.execute("""
        SELECT sub.subject_code, sub.subject_name, sub.subject_type,
               COUNT(a.attendance_id) AS total_sessions,
               SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS present_count
        FROM subject sub
        LEFT JOIN class_session cs ON sub.subject_id = cs.subject_id
        LEFT JOIN attendance a ON cs.session_id = a.session_id AND a.student_id = %s
        GROUP BY sub.subject_id, sub.subject_code, sub.subject_name, sub.subject_type
        LIMIT 6
    """, (student_id,))
    attendance_subjects = cursor.fetchall()
    for s in attendance_subjects:
        tot = s['total_sessions'] or 0
        prs = s['present_count'] or 0
        s['pct'] = round((prs / tot * 100), 1) if tot > 0 else 94.29
        s['status_tag'] = 'Eligible' if s['pct'] >= 75 else 'Not-Eligible'

    # Syllabus completion metrics for dashboard graph
    cursor.execute("""
        SELECT sub.subject_code, COALESCE(st.completion_pct, 85.0) AS completion_pct
        FROM subject sub
        LEFT JOIN syllabus_tracker st ON sub.subject_id = st.subject_id
        ORDER BY sub.subject_code
        LIMIT 6
    """)
    syllabus_graph_data = cursor.fetchall()

    # Recent Lost & Found items
    cursor.execute("""
        SELECT item_id, item_type, title, category, location, current_custody, item_status
        FROM lost_found_item
        ORDER BY created_at DESC
        LIMIT 3
    """)
    recent_lost_found = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/dashboard.html',
                           student=student,
                           att_pct=round(att_pct, 1),
                           total_sess=total_sess,
                           pres_count=pres_count,
                           avg_score=round(avg_score, 1),
                           earned_credits=earned_credits,
                           total_degree_credits=total_degree_credits,
                           completion_pct=completion_pct,
                           total_due=total_due,
                           today_classes=today_classes,
                           open_drives=open_drives,
                           pending_leaves=pending_leaves,
                           notices=notices,
                           attendance_subjects=attendance_subjects,
                           syllabus_graph_data=syllabus_graph_data,
                           recent_lost_found=recent_lost_found,
                           sgpa=9.07)


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

    # Fetch Documents in Digital Locker
    documents = []
    if profile:
        cursor.execute("""
            SELECT doc_id, doc_type, doc_title, file_name, file_size_kb, upload_date, verification_status, verified_by
            FROM student_document
            WHERE student_id = %s
            ORDER BY doc_id ASC
        """, (profile['student_id'],))
        documents = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('student/profile.html', profile=profile, documents=documents)


@app.route('/student/upload-document', methods=['POST'])
@login_required(['STUDENT'])
def student_upload_document():
    user_id = session['user']['user_id']
    doc_type = request.form.get('doc_type')
    doc_title = request.form.get('doc_title')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    stu = cursor.fetchone()

    if stu and doc_type and doc_title:
        file_name = f"{doc_type}_{stu['student_id']}_verified.pdf"
        cursor.execute("""
            INSERT INTO student_document (student_id, doc_type, doc_title, file_name, file_size_kb, upload_date, verification_status, verified_by)
            VALUES (%s, %s, %s, %s, 1420, CURRENT_DATE, 'UNDER_REVIEW', 'Academic Verification Cell')
        """, (stu['student_id'], doc_type, doc_title, file_name))
        conn.commit()
        log_audit(user_id, 'INSERT', 'student_document', cursor.lastrowid, f"Uploaded document {doc_title}")
        flash(f"Document '{doc_title}' uploaded to Digital Vault for verification!", "success")

    cursor.close()
    conn.close()
    return redirect(url_for('student_profile'))


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

    # Credit Breakdown for Course Completion Graph
    credit_stats = {
        'earned_core': 64,
        'earned_elective': 24,
        'earned_lab': 16,
        'earned_mooc': 6,
        'total_earned': 110,
        'total_required': 160,
        'completion_pct': 68.8
    }

    return render_template('student/academics.html', enrollments=enrollments, marks=marks_list, credit_stats=credit_stats)


@app.route('/student/mooc-quizzes')
@login_required(['STUDENT'])
def student_mooc_quizzes():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    moocs = []
    quizzes = []
    attempts = []

    if student:
        cursor.execute("""
            SELECT mooc_id, course_title, platform, instructor, duration_weeks, credits, status, progress_pct, completion_date, grade, certificate_id
            FROM mooc_course
            WHERE student_id = %s
            ORDER BY status DESC
        """, (student['student_id'],))
        moocs = cursor.fetchall()

        cursor.execute("""
            SELECT sq.quiz_id, sq.title, sq.topic, sq.duration_minutes, sq.total_questions, sq.max_marks, sq.difficulty,
                   sub.subject_code, sub.subject_name
            FROM student_quiz sq
            JOIN subject sub ON sq.subject_id = sub.subject_id
            ORDER BY sq.quiz_id ASC
        """)
        quizzes = cursor.fetchall()

        cursor.execute("""
            SELECT qa.attempt_id, qa.score, qa.max_score, qa.percentage, qa.status, qa.completed_at,
                   sq.title AS quiz_title
            FROM quiz_attempt qa
            JOIN student_quiz sq ON qa.quiz_id = sq.quiz_id
            WHERE qa.student_id = %s
            ORDER BY qa.completed_at DESC
        """, (student['student_id'],))
        attempts = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('student/mooc_quizzes.html', moocs=moocs, quizzes=quizzes, attempts=attempts)


@app.route('/student/take-quiz/<int:quiz_id>', methods=['POST'])
@login_required(['STUDENT'])
def take_quiz(quiz_id):
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    if student:
        cursor.execute("SELECT max_marks FROM student_quiz WHERE quiz_id = %s", (quiz_id,))
        quiz = cursor.fetchone()
        max_marks = quiz['max_marks'] if quiz else 20
        simulated_score = max_marks - 2  # high performance
        pct = round((simulated_score / max_marks) * 100, 1)

        cursor.execute("""
            INSERT INTO quiz_attempt (quiz_id, student_id, score, max_score, percentage, status)
            VALUES (%s, %s, %s, %s, %s, 'PASSED')
        """, (quiz_id, student['student_id'], simulated_score, max_marks, pct))
        conn.commit()
        log_audit(user_id, 'INSERT', 'quiz_attempt', cursor.lastrowid, f"Completed online quiz ID {quiz_id} with score {simulated_score}/{max_marks}")
        flash(f"🎉 Quiz Completed! You scored {simulated_score}/{max_marks} ({pct}%) - PASSED!", "success")

    cursor.close()
    conn.close()
    return redirect(url_for('student_mooc_quizzes'))


@app.route('/student/fees')
@login_required(['STUDENT'])
def student_fees():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    fee_records = []
    total_billed = 0
    total_paid = 0
    total_due = 0

    if student:
        cursor.execute("""
            SELECT fee_id, semester, academic_year, tuition_fee, exam_fee, library_fee,
                   total_amount, paid_amount, due_amount, status, payment_date,
                   transaction_ref, payment_mode, receipt_no, created_at
            FROM student_fee
            WHERE student_id = %s
            ORDER BY semester DESC
        """, (student['student_id'],))
        fee_records = cursor.fetchall()

        for f in fee_records:
            total_billed += float(f['total_amount'])
            total_paid += float(f['paid_amount'])
            total_due += float(f['due_amount'])

    cursor.close()
    conn.close()

    return render_template('student/fees.html',
                           fee_records=fee_records,
                           total_billed=total_billed,
                           total_paid=total_paid,
                           total_due=total_due)


@app.route('/student/pay-fee/<int:fee_id>', methods=['POST'])
@login_required(['STUDENT'])
def pay_fee(fee_id):
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT total_amount FROM student_fee WHERE fee_id = %s", (fee_id,))
    fee = cursor.fetchone()

    if fee:
        txn_id = f"TXN-NET-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        rcp_no = f"RCP-2026-ONLINE-{fee_id:04d}"
        cursor.execute("""
            UPDATE student_fee
            SET paid_amount = total_amount, due_amount = 0.0, status = 'PAID',
                payment_date = CURRENT_DATE, transaction_ref = %s, payment_mode = 'UPI', receipt_no = %s
            WHERE fee_id = %s
        """, (txn_id, rcp_no, fee_id))
        conn.commit()
        log_audit(user_id, 'UPDATE', 'student_fee', fee_id, f"Fee payment processed successfully for fee ID {fee_id}")
        flash(f"Payment successful! Receipt {rcp_no} generated.", "success")

    cursor.close()
    conn.close()
    return redirect(url_for('student_fees'))


@app.route('/student/schedule')
@login_required(['STUDENT'])
def student_schedule():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Class timetable grouped by day
    cursor.execute("""
        SELECT ct.timetable_id, ct.day_of_week, ct.start_time, ct.end_time, ct.room_no, ct.session_type,
               sub.subject_code, sub.subject_name,
               u.first_name, u.last_name
        FROM class_timetable ct
        JOIN subject sub ON ct.subject_id = sub.subject_id
        JOIN faculty f ON ct.faculty_id = f.faculty_id
        JOIN users u ON f.user_id = u.user_id
        ORDER BY FIELD(ct.day_of_week, 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY'), ct.start_time ASC
    """)
    timetable_rows = cursor.fetchall()

    timetable = {}
    for r in timetable_rows:
        day = r['day_of_week']
        if day not in timetable:
            timetable[day] = []
        timetable[day].append(r)

    # Upcoming exam schedule
    cursor.execute("""
        SELECT es.exam_id, es.exam_type, es.exam_date, es.start_time, es.end_time, es.room_no, es.max_marks, es.syllabus_scope,
               sub.subject_code, sub.subject_name
        FROM exam_schedule es
        JOIN subject sub ON es.subject_id = sub.subject_id
        ORDER BY es.exam_date ASC
    """)
    exam_schedule = cursor.fetchall()

    # Academic calendar & holidays
    cursor.execute("""
        SELECT event_id, title, event_type, start_date, end_date, description, is_national_holiday
        FROM academic_calendar
        ORDER BY start_date ASC
    """)
    calendar_events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/schedule.html',
                           timetable=timetable,
                           exam_schedule=exam_schedule,
                           calendar_events=calendar_events)


@app.route('/student/placements')
@login_required(['STUDENT'])
def student_placements():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, d.department_name, u.first_name, u.last_name, u.email, u.phone
        FROM student s
        JOIN users u ON s.user_id = u.user_id
        LEFT JOIN department d ON s.department_id = d.department_id
        WHERE s.user_id = %s
    """, (user_id,))
    student = cursor.fetchone()

    drives = []
    applications = []

    if student:
        cursor.execute("""
            SELECT d.drive_id, d.drive_title AS job_title, d.role_description AS job_description,
                   d.package_in_lpa AS package_lpa, d.job_location, d.job_role,
                   d.minimum_cgpa, d.minimum_10th_percentage, d.minimum_12th_percentage, d.maximum_backlogs,
                   d.eligible_degree, d.eligible_branch,
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
                   d.drive_title AS job_title, d.package_in_lpa AS package_lpa, c.company_name, d.job_location
            FROM student_application sa
            JOIN drive d ON sa.drive_id = d.drive_id
            JOIN company c ON d.company_id = c.company_id
            WHERE sa.student_id = %s
            ORDER BY sa.applied_at DESC
        """, (student['student_id'],))
        applications = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('student/placements.html', drives=drives, applications=applications, student=student)


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


@app.route('/lost-found', methods=['GET', 'POST'])
@login_required()
def lost_found_hub():
    user = session['user']
    user_id = user['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        item_type = request.form.get('item_type', 'FOUND')
        title = request.form.get('title')
        category = request.form.get('category', 'OTHER')
        description = request.form.get('description')
        location = request.form.get('location')
        current_custody = request.form.get('current_custody')
        contact_info = request.form.get('contact_info', user.get('email', ''))

        if not title or not description or not location or not current_custody:
            flash("Please fill in all mandatory fields to post the item.", "danger")
        else:
            cursor.execute("""
                INSERT INTO lost_found_item (item_type, title, category, description, location, current_custody, reported_by, contact_info, item_status, reported_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'AVAILABLE', CURRENT_DATE)
            """, (item_type, title, category, description, location, current_custody, user_id, contact_info))
            conn.commit()
            log_audit(user_id, 'INSERT', 'lost_found_item', cursor.lastrowid, f"Reported {item_type} item: {title}")
            flash("🎉 Item successfully posted to Campus Lost & Found repository!", "success")
            return redirect(url_for('lost_found_hub'))

    filter_type = request.args.get('type', 'ALL')
    filter_cat = request.args.get('category', 'ALL')
    search_q = request.args.get('q', '').strip()

    query = """
        SELECT lf.*, u.first_name, u.last_name, u.role
        FROM lost_found_item lf
        JOIN users u ON lf.reported_by = u.user_id
        WHERE 1=1
    """
    params = []

    if filter_type in ['FOUND', 'LOST']:
        query += " AND lf.item_type = %s"
        params.append(filter_type)
    if filter_cat != 'ALL':
        query += " AND lf.category = %s"
        params.append(filter_cat)
    if search_q:
        query += " AND (lf.title LIKE %s OR lf.description LIKE %s OR lf.location LIKE %s OR lf.current_custody LIKE %s)"
        like_term = f"%{search_q}%"
        params.extend([like_term, like_term, like_term, like_term])

    query += " ORDER BY lf.created_at DESC"
    cursor.execute(query, tuple(params))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('lost_found.html', items=items, filter_type=filter_type, filter_cat=filter_cat, search_q=search_q)


@app.route('/lost-found/update-status/<int:item_id>', methods=['POST'])
@login_required()
def lost_found_update_status(item_id):
    user_id = session['user']['user_id']
    new_status = request.form.get('item_status')
    new_custody = request.form.get('current_custody')

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if new_status:
        if new_custody:
            cursor.execute("""
                UPDATE lost_found_item
                SET item_status = %s, current_custody = %s
                WHERE item_id = %s
            """, (new_status, new_custody, item_id))
        else:
            cursor.execute("""
                UPDATE lost_found_item
                SET item_status = %s
                WHERE item_id = %s
            """, (new_status, item_id))
        conn.commit()
        log_audit(user_id, 'UPDATE', 'lost_found_item', item_id, f"Updated status of item {item_id} to {new_status}")
        flash(f"Item status successfully updated to {new_status.replace('_', ' ')}!", "success")

    cursor.close()
    conn.close()
    return redirect(url_for('lost_found_hub'))


@app.route('/student/hall-ticket')
@login_required(['STUDENT'])
def student_hall_ticket():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.student_id, s.enrollment_number, s.blood_group,
               u.first_name, u.middle_name, u.last_name, u.email, u.phone,
               d.department_name, d.department_code,
               c.course_name, c.course_code,
               se.semester AS current_semester, se.enrollment_date
        FROM student s
        JOIN users u ON s.user_id = u.user_id
        JOIN department d ON s.department_id = d.department_id
        LEFT JOIN student_enrollment se ON s.student_id = se.student_id
        LEFT JOIN course c ON se.course_id = c.course_id
        WHERE u.user_id = %s
    """, (user_id,))
    student = cursor.fetchone()

    cursor.execute("""
        SELECT es.exam_id, es.exam_type, es.exam_date, es.start_time, es.end_time, es.room_no, es.max_marks,
               sub.subject_code, sub.subject_name, sub.credits
        FROM exam_schedule es
        JOIN subject sub ON es.subject_id = sub.subject_id
        ORDER BY es.exam_date ASC, es.start_time ASC
    """)
    exam_papers = cursor.fetchall()

    cursor.close()
    conn.close()

    seat_no = f"WPU-2026-CSE-{student['student_id']:04d}" if student else "WPU-2026-CSE-0001"
    center_code = "CENTER-04 (School of Computer Science & Engineering, Punecity Campus)"

    return render_template('student/hall_ticket.html',
                           student=student,
                           exam_papers=exam_papers,
                           seat_no=seat_no,
                           center_code=center_code)


@app.route('/student/syllabus')
@login_required(['STUDENT'])
def student_syllabus():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT sub.subject_id, sub.subject_code, sub.subject_name, sub.credits, sub.semester, sub.subject_type,
               COALESCE(st.total_units, 5) AS total_units,
               COALESCE(st.completed_units, 4) AS completed_units,
               COALESCE(st.completion_pct, 80.0) AS completion_pct,
               COALESCE(st.last_updated, CURRENT_DATE) AS last_updated
        FROM subject sub
        LEFT JOIN syllabus_tracker st ON sub.subject_id = st.subject_id
        ORDER BY sub.subject_code ASC
    """)
    syllabus_list = cursor.fetchall()

    cursor.close()
    conn.close()

    unit_breakdown = {
        'CSE3001': [
            {'unit': 1, 'title': 'Introduction & Heuristic Search Strategies', 'hours': 8, 'status': 'COMPLETED'},
            {'unit': 2, 'title': 'Knowledge Representation & First-Order Logic', 'hours': 10, 'status': 'COMPLETED'},
            {'unit': 3, 'title': 'Probabilistic Reasoning & Bayesian Networks', 'hours': 9, 'status': 'COMPLETED'},
            {'unit': 4, 'title': 'Machine Learning Fundamentals & Decision Trees', 'hours': 9, 'status': 'COMPLETED'},
            {'unit': 5, 'title': 'Expert System Shells & Rule-Based Inference Engines', 'hours': 8, 'status': 'IN_PROGRESS'}
        ],
        'CSE3002': [
            {'unit': 1, 'title': 'Cloud Virtualization & Hypervisor Architecture', 'hours': 8, 'status': 'COMPLETED'},
            {'unit': 2, 'title': 'IaaS, PaaS, SaaS Services & Cloud Security', 'hours': 10, 'status': 'COMPLETED'},
            {'unit': 3, 'title': 'Docker Containerization & Kubernetes Orchestration', 'hours': 12, 'status': 'COMPLETED'},
            {'unit': 4, 'title': 'CI/CD Pipelines, GitHub Actions & Terraform IaC', 'hours': 8, 'status': 'COMPLETED'},
            {'unit': 5, 'title': 'Serverless Microservices & Cloud Monitoring', 'hours': 6, 'status': 'COMPLETED'}
        ],
        'CSE2011': [
            {'unit': 1, 'title': 'OSI & TCP/IP Reference Architectures', 'hours': 8, 'status': 'COMPLETED'},
            {'unit': 2, 'title': 'Data Link Layer, Framing & Error Control Protocols', 'hours': 10, 'status': 'COMPLETED'},
            {'unit': 3, 'title': 'Network Layer Routing Algorithms (OSPF, BGP)', 'hours': 10, 'status': 'COMPLETED'},
            {'unit': 4, 'title': 'Transport Layer Congestion & Flow Control (TCP/UDP)', 'hours': 8, 'status': 'COMPLETED'},
            {'unit': 5, 'title': 'Application Layer Protocols & Cryptographic Security', 'hours': 8, 'status': 'IN_PROGRESS'}
        ]
    }

    return render_template('student/syllabus.html', syllabus_list=syllabus_list, unit_breakdown=unit_breakdown)


@app.route('/student/library', methods=['GET', 'POST'])
@login_required(['STUDENT'])
def student_library():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    if request.method == 'POST' and student:
        book_id = request.form.get('book_id')
        action_type = request.form.get('action_type', 'RESERVE')
        cursor.execute("SELECT title, available_copies FROM library_book WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        if book:
            if action_type == 'RESERVE':
                flash(f"📘 Reservation request submitted for '{book['title']}'. You will receive a notification when ready for pickup at the circulation desk.", "success")
            elif action_type == 'RENEW':
                flash(f"🔄 Renewal requested for '{book['title']}'. Extended by 14 days.", "success")
            log_audit(user_id, 'ACTION', 'library_book', book_id, f"{action_type} book: {book['title']}")

    cursor.execute("""
        SELECT book_id, isbn, title, author, category, shelf_location, available_copies, total_copies
        FROM library_book
        ORDER BY title ASC
    """)
    books = cursor.fetchall()

    my_issues = []
    if student:
        cursor.execute("""
            SELECT li.issue_id, li.issue_date, li.due_date, li.return_date, li.status, li.fine_amount,
                   lb.title, lb.author, lb.isbn, lb.shelf_location
            FROM library_issue li
            JOIN library_book lb ON li.book_id = lb.book_id
            WHERE li.student_id = %s
            ORDER BY li.issue_date DESC
        """, (student['student_id'],))
        my_issues = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/library.html', books=books, my_issues=my_issues)


@app.route('/student/cbcs', methods=['GET', 'POST'])
@login_required(['STUDENT'])
def student_cbcs():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT student_id FROM student WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    if request.method == 'POST' and student:
        pe_id = request.form.get('pe_subject_id')
        oe_id = request.form.get('oe_subject_id')

        if pe_id:
            cursor.execute("""
                INSERT INTO cbcs_elective_choice (student_id, academic_year, semester, elective_type, subject_id, status)
                VALUES (%s, '2025-26', 5, 'PROFESSIONAL_ELECTIVE', %s, 'SUBMITTED')
                ON DUPLICATE KEY UPDATE subject_id = VALUES(subject_id), status = 'SUBMITTED'
            """, (student['student_id'], pe_id))
        if oe_id:
            cursor.execute("""
                INSERT INTO cbcs_elective_choice (student_id, academic_year, semester, elective_type, subject_id, status)
                VALUES (%s, '2025-26', 5, 'OPEN_ELECTIVE', %s, 'SUBMITTED')
                ON DUPLICATE KEY UPDATE subject_id = VALUES(subject_id), status = 'SUBMITTED'
            """, (student['student_id'], oe_id))
        conn.commit()
        log_audit(user_id, 'UPDATE', 'cbcs_elective_choice', student['student_id'], "Submitted CBCS elective choices")
        flash("🎉 CBCS Elective choices submitted successfully! Department review in progress.", "success")
        return redirect(url_for('student_cbcs'))

    cursor.execute("""
        SELECT subject_id, subject_code, subject_name, credits, semester, subject_type
        FROM subject
        WHERE subject_code LIKE 'PE%' OR subject_code LIKE 'OE%'
        ORDER BY subject_code
    """)
    elective_subjects = cursor.fetchall()

    current_choices = []
    if student:
        cursor.execute("""
            SELECT c.choice_id, c.academic_year, c.semester, c.elective_type, c.status, c.created_at,
                   sub.subject_code, sub.subject_name, sub.credits
            FROM cbcs_elective_choice c
            JOIN subject sub ON c.subject_id = sub.subject_id
            WHERE c.student_id = %s
        """, (student['student_id'],))
        current_choices = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/cbcs.html', elective_subjects=elective_subjects, current_choices=current_choices)


@app.route('/student/support', methods=['GET', 'POST'])
@login_required(['STUDENT'])
def student_support():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        category = request.form.get('category', 'GENERAL')
        subject = request.form.get('subject')
        description = request.form.get('description')
        priority = request.form.get('priority', 'MEDIUM')

        if not subject or not description:
            flash("Subject and description are required to raise a ticket.", "danger")
        else:
            cursor.execute("""
                INSERT INTO student_support_ticket (user_id, category, subject, description, priority, status)
                VALUES (%s, %s, %s, %s, %s, 'OPEN')
            """, (user_id, category, subject, description, priority))
            conn.commit()
            log_audit(user_id, 'INSERT', 'student_support_ticket', cursor.lastrowid, f"Submitted support ticket: {subject}")
            flash("🎫 Support ticket submitted! Academic Helpdesk will respond within 24 business hours.", "success")
            return redirect(url_for('student_support'))

    cursor.execute("""
        SELECT ticket_id, category, subject, description, priority, status, admin_response, created_at, resolved_at
        FROM student_support_ticket
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student/support.html', tickets=tickets)


@app.route('/student/update-request', methods=['GET', 'POST'])
@login_required(['STUDENT'])
def student_update_request():
    user_id = session['user']['user_id']
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        field_name = request.form.get('field_name')
        new_value = request.form.get('new_value')
        justification = request.form.get('justification')

        if not field_name or not new_value:
            flash("Field name and requested value are required.", "danger")
        else:
            subj = f"Official Record Updation Request: {field_name.replace('_', ' ').title()}"
            desc = f"Requested Change: Set {field_name} to '{new_value}'.\nReason/Justification: {justification or 'Student self-service update'}"
            cursor.execute("""
                INSERT INTO student_support_ticket (user_id, category, subject, description, priority, status)
                VALUES (%s, 'GENERAL', %s, %s, 'MEDIUM', 'OPEN')
            """, (user_id, subj, desc))
            conn.commit()
            log_audit(user_id, 'INSERT', 'student_support_ticket', cursor.lastrowid, f"Submitted record update request for {field_name}")
            flash(f"Updation request for {field_name.replace('_', ' ')} submitted to Registrar Office!", "success")
            return redirect(url_for('student_profile'))

    cursor.close()
    conn.close()
    return redirect(url_for('student_profile'))


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
