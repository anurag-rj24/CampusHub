from database.connection import create_connection
from utils.password import hash_password

def expand_db():
    conn = create_connection()
    cur = conn.cursor(dictionary=True)
    h = hash_password('test123')

    # 1. Create student_document table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_document (
            doc_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id BIGINT NOT NULL,
            doc_type ENUM('AADHAAR', '10TH_MARKSHEET', '12TH_MARKSHEET', 'BIRTH_CERTIFICATE', 'DOMICILE_CERTIFICATE', 'TRANSFER_CERTIFICATE', 'INCOME_CERTIFICATE') NOT NULL,
            doc_title VARCHAR(150) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_size_kb INT DEFAULT 1024,
            upload_date DATE NOT NULL,
            verification_status ENUM('VERIFIED', 'UNDER_REVIEW', 'REJECTED') DEFAULT 'VERIFIED',
            verified_by VARCHAR(100) DEFAULT 'Registrar Office',
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 2. Create student_fee table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_fee (
            fee_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id BIGINT NOT NULL,
            semester INT NOT NULL,
            academic_year VARCHAR(20) NOT NULL,
            tuition_fee DECIMAL(10,2) NOT NULL,
            exam_fee DECIMAL(10,2) NOT NULL,
            library_fee DECIMAL(10,2) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            paid_amount DECIMAL(10,2) NOT NULL,
            due_amount DECIMAL(10,2) NOT NULL,
            status ENUM('PAID', 'PARTIAL', 'DUE', 'OVERDUE') NOT NULL,
            payment_date DATE,
            transaction_ref VARCHAR(100),
            payment_mode ENUM('UPI', 'NET_BANKING', 'CREDIT_CARD', 'DEBIT_CARD', 'DEMAND_DRAFT'),
            receipt_no VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 3. Create mooc_course table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mooc_course (
            mooc_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id BIGINT NOT NULL,
            course_title VARCHAR(200) NOT NULL,
            platform ENUM('NPTEL', 'COURSERA', 'SWAYAM', 'EDX', 'UDEMY') NOT NULL,
            instructor VARCHAR(150) NOT NULL,
            duration_weeks INT NOT NULL,
            credits INT DEFAULT 3,
            status ENUM('COMPLETED', 'IN_PROGRESS', 'ENROLLED') NOT NULL,
            progress_pct INT DEFAULT 0,
            completion_date DATE,
            grade VARCHAR(50),
            certificate_id VARCHAR(100),
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    cur.execute("ALTER TABLE mooc_course MODIFY grade VARCHAR(50);")

    # 4. Create student_quiz table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_quiz (
            quiz_id INT AUTO_INCREMENT PRIMARY KEY,
            subject_id INT NOT NULL,
            title VARCHAR(200) NOT NULL,
            topic VARCHAR(150) NOT NULL,
            duration_minutes INT DEFAULT 20,
            total_questions INT DEFAULT 10,
            max_marks INT DEFAULT 20,
            difficulty ENUM('BEGINNER', 'INTERMEDIATE', 'ADVANCED') DEFAULT 'INTERMEDIATE',
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 5. Create quiz_attempt table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempt (
            attempt_id INT AUTO_INCREMENT PRIMARY KEY,
            quiz_id INT NOT NULL,
            student_id BIGINT NOT NULL,
            score INT NOT NULL,
            max_score INT NOT NULL,
            percentage DECIMAL(5,2) NOT NULL,
            status ENUM('PASSED', 'FAILED') NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES student_quiz(quiz_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 6. Create academic_calendar table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS academic_calendar (
            event_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            event_type ENUM('HOLIDAY', 'EXAM', 'ACADEMIC_EVENT', 'FESTIVAL', 'WORKSHOP', 'VACATION') NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            description TEXT,
            is_national_holiday BOOLEAN DEFAULT FALSE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 7. Create exam_schedule table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exam_schedule (
            exam_id INT AUTO_INCREMENT PRIMARY KEY,
            subject_id INT NOT NULL,
            exam_type ENUM('MID_TERM', 'END_TERM', 'PRACTICAL_VIVA') NOT NULL,
            exam_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            room_no VARCHAR(50) NOT NULL,
            max_marks INT DEFAULT 100,
            syllabus_scope VARCHAR(255) DEFAULT 'Full Syllabus Unit 1-5',
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 8. Create class_timetable table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS class_timetable (
            timetable_id INT AUTO_INCREMENT PRIMARY KEY,
            department_id INT NOT NULL,
            semester INT NOT NULL,
            day_of_week ENUM('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY') NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            subject_id INT NOT NULL,
            faculty_id BIGINT NOT NULL,
            room_no VARCHAR(50) NOT NULL,
            session_type ENUM('LECTURE', 'LAB', 'TUTORIAL') NOT NULL,
            FOREIGN KEY (department_id) REFERENCES department(department_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subject(subject_id) ON DELETE CASCADE,
            FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    conn.commit()

    # --- POPULATE SEED DATA ---

    # Check student
    cur.execute("SELECT student_id, user_id FROM student WHERE user_id = 1")
    stu = cur.fetchone()
    if stu:
        sid = stu['student_id']

        # Seed Documents
        cur.execute("SELECT COUNT(*) AS c FROM student_document WHERE student_id = %s", (sid,))
        if cur.fetchone()['c'] == 0:
            docs = [
                (sid, 'AADHAAR', 'Aadhaar Identity Card (Govt of India)', 'Aadhaar_UIDAI_8921.pdf', 1240, '2024-07-15', 'VERIFIED'),
                (sid, '10TH_MARKSHEET', 'Secondary School Certificate (Class 10)', 'CBSE_10th_Marksheet.pdf', 2150, '2024-07-15', 'VERIFIED'),
                (sid, '12TH_MARKSHEET', 'Senior Secondary Marksheet (Class 12)', 'CBSE_12th_Passing.pdf', 2340, '2024-07-15', 'VERIFIED'),
                (sid, 'BIRTH_CERTIFICATE', 'Official Municipal Birth Certificate', 'Birth_Certificate_Municipal.pdf', 980, '2024-07-16', 'VERIFIED'),
                (sid, 'DOMICILE_CERTIFICATE', 'State Domicile & Residence Certificate', 'State_Domicile_Cert_2024.pdf', 1450, '2024-07-16', 'VERIFIED'),
                (sid, 'TRANSFER_CERTIFICATE', 'School Transfer & Migration Certificate', 'School_TC_Migration.pdf', 860, '2024-07-18', 'VERIFIED'),
            ]
            cur.executemany("""
                INSERT INTO student_document (student_id, doc_type, doc_title, file_name, file_size_kb, upload_date, verification_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, docs)

        # Seed Fees
        cur.execute("SELECT COUNT(*) AS c FROM student_fee WHERE student_id = %s", (sid,))
        if cur.fetchone()['c'] == 0:
            fees = [
                (sid, 1, '2024-25', 65000.0, 3500.0, 1500.0, 70000.0, 70000.0, 0.0, 'PAID', '2024-08-05', 'TXN-HDFC-99824102', 'NET_BANKING', 'RCP-2024-SEM1-00892'),
                (sid, 2, '2024-25', 65000.0, 3500.0, 1500.0, 70000.0, 70000.0, 0.0, 'PAID', '2025-01-12', 'TXN-UPI-77402911', 'UPI', 'RCP-2025-SEM2-01435'),
                (sid, 3, '2025-26', 68000.0, 4000.0, 1500.0, 73500.0, 73500.0, 0.0, 'PAID', '2025-07-20', 'TXN-CARD-88392019', 'CREDIT_CARD', 'RCP-2025-SEM3-02194'),
                (sid, 4, '2025-26', 68000.0, 4000.0, 1500.0, 73500.0, 35000.0, 38500.0, 'PARTIAL', '2026-01-15', 'TXN-UPI-99201948', 'UPI', 'RCP-2026-SEM4-03011'),
            ]
            cur.executemany("""
                INSERT INTO student_fee (student_id, semester, academic_year, tuition_fee, exam_fee, library_fee, total_amount, paid_amount, due_amount, status, payment_date, transaction_ref, payment_mode, receipt_no)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, fees)

        # Seed MOOC Courses
        cur.execute("SELECT COUNT(*) AS c FROM mooc_course WHERE student_id = %s", (sid,))
        if cur.fetchone()['c'] == 0:
            moocs = [
                (sid, 'Cloud Computing & Distributed Systems', 'NPTEL', 'Prof. Rajiv Misra (IIT Patna)', 12, 3, 'COMPLETED', 100, '2025-11-20', 'Elite+Gold (94%)', 'NPTEL-2025-CS892'),
                (sid, 'Deep Learning Specialization (5-Course Series)', 'COURSERA', 'Andrew Ng (DeepLearning.AI)', 16, 4, 'COMPLETED', 100, '2025-12-15', 'Grade A+ (98%)', 'COURSERA-DL-99201'),
                (sid, 'Applied Data Structures and Algorithms in C++', 'SWAYAM', 'Prof. Naveen Garg (IIT Delhi)', 12, 3, 'IN_PROGRESS', 72, None, 'On Track (A)', None),
                (sid, 'Full-Stack Modern Web Engineering with React & Node', 'EDX', 'HarvardX / edX Staff', 10, 3, 'IN_PROGRESS', 45, None, 'In Progress', None),
            ]
            cur.executemany("""
                INSERT INTO mooc_course (student_id, course_title, platform, instructor, duration_weeks, credits, status, progress_pct, completion_date, grade, certificate_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, moocs)

    # Seed Academic Calendar Events
    cur.execute("SELECT COUNT(*) AS c FROM academic_calendar")
    if cur.fetchone()['c'] == 0:
        events = [
            ('Commencement of Academic Session 2025-26 (Even Semester)', 'ACADEMIC_EVENT', '2026-01-05', '2026-01-05', 'All classes and labs commence across departments.', False),
            ('Republic Day National Holiday', 'HOLIDAY', '2026-01-26', '2026-01-26', 'National Holiday - Campus Administrative Closure.', True),
            ('Mid-Semester Assessment & Theory Examinations', 'EXAM', '2026-03-02', '2026-03-09', 'Mid-Term tests for all undergraduate and postgraduate batches.', False),
            ('Annual Technical & Innovation Symposium (TechFest 2026)', 'FESTIVAL', '2026-03-18', '2026-03-20', 'Flagship university-wide hackathons, robotics, and project exhibition.', False),
            ('Holi Spring Festival Break', 'HOLIDAY', '2026-03-25', '2026-03-26', 'Gazetted Holiday for Holi Festival.', True),
            ('Course Completion & End-Term Project Submissions', 'ACADEMIC_EVENT', '2026-04-20', '2026-04-25', 'Submission of lab journals, capstone projects, and attendance freeze.', False),
            ('End-Semester Final University Theory Examinations', 'EXAM', '2026-05-04', '2026-05-22', 'Final regular & backlog theory examinations for all semesters.', False),
            ('Summer Vacation & Industrial Internship Period', 'VACATION', '2026-05-25', '2026-07-15', 'Summer break and mandatory industry internship tenure.', False),
        ]
        cur.executemany("""
            INSERT INTO academic_calendar (title, event_type, start_date, end_date, description, is_national_holiday)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, events)

    # Ensure Subjects exist
    cur.execute("SELECT subject_id FROM subject LIMIT 4")
    subs = [s['subject_id'] for s in cur.fetchall()]

    if subs:
        # Seed Exam Schedule
        cur.execute("SELECT COUNT(*) AS c FROM exam_schedule")
        if cur.fetchone()['c'] == 0:
            exams = [
                (subs[0], 'MID_TERM', '2026-03-02', '09:30:00', '11:30:00', 'Exam Hall 101', 50, 'Units 1, 2, and 3'),
                (subs[1] if len(subs) > 1 else subs[0], 'MID_TERM', '2026-03-04', '09:30:00', '11:30:00', 'Exam Hall 102', 50, 'Units 1, 2, and 3'),
                (subs[2] if len(subs) > 2 else subs[0], 'MID_TERM', '2026-03-06', '14:00:00', '16:00:00', 'Exam Hall 201', 50, 'Units 1, 2, and 3'),
                (subs[0], 'END_TERM', '2026-05-04', '09:30:00', '12:30:00', 'Auditorium Block A', 100, 'Comprehensive Syllabus (Units 1-5)'),
                (subs[1] if len(subs) > 1 else subs[0], 'END_TERM', '2026-05-08', '09:30:00', '12:30:00', 'Auditorium Block A', 100, 'Comprehensive Syllabus (Units 1-5)'),
            ]
            cur.executemany("""
                INSERT INTO exam_schedule (subject_id, exam_type, exam_date, start_time, end_time, room_no, max_marks, syllabus_scope)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, exams)

        # Seed Quizzes
        cur.execute("SELECT COUNT(*) AS c FROM student_quiz")
        if cur.fetchone()['c'] == 0:
            quizzes = [
                (subs[0], 'Relational DBMS & SQL Optimization Quiz', 'SQL Indexing & Normalization', 20, 10, 20, 'INTERMEDIATE'),
                (subs[1] if len(subs) > 1 else subs[0], 'Operating Systems Processes & Memory Quiz', 'Process Synchronization & Paging', 25, 15, 30, 'ADVANCED'),
                (subs[2] if len(subs) > 2 else subs[0], 'Computer Networks Protocols & Routing Quiz', 'TCP/IP & Routing Algorithms', 20, 10, 20, 'INTERMEDIATE'),
            ]
            cur.executemany("""
                INSERT INTO student_quiz (subject_id, title, topic, duration_minutes, total_questions, max_marks, difficulty)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, quizzes)

            # Add sample passed attempts for student
            if stu:
                cur.execute("SELECT quiz_id FROM student_quiz LIMIT 2")
                q_ids = [q['quiz_id'] for q in cur.fetchall()]
                if q_ids:
                    cur.execute("""
                        INSERT INTO quiz_attempt (quiz_id, student_id, score, max_score, percentage, status)
                        VALUES (%s, %s, 18, 20, 90.0, 'PASSED'), (%s, %s, 27, 30, 90.0, 'PASSED')
                    """, (q_ids[0], stu['student_id'], q_ids[1] if len(q_ids) > 1 else q_ids[0], stu['student_id']))

        # Seed Timetable
        cur.execute("SELECT faculty_id FROM faculty LIMIT 1")
        fac = cur.fetchone()
        fid = fac['faculty_id'] if fac else 1

        cur.execute("SELECT COUNT(*) AS c FROM class_timetable")
        if cur.fetchone()['c'] == 0:
            tt = [
                (1, 4, 'MONDAY', '09:00:00', '10:00:00', subs[0], fid, 'Room 301', 'LECTURE'),
                (1, 4, 'MONDAY', '10:00:00', '11:00:00', subs[1] if len(subs) > 1 else subs[0], fid, 'Room 301', 'LECTURE'),
                (1, 4, 'MONDAY', '11:15:00', '13:15:00', subs[0], fid, 'Computer Lab 3', 'LAB'),
                (1, 4, 'TUESDAY', '09:00:00', '10:00:00', subs[2] if len(subs) > 2 else subs[0], fid, 'Room 302', 'LECTURE'),
                (1, 4, 'TUESDAY', '10:00:00', '11:00:00', subs[0], fid, 'Room 302', 'LECTURE'),
                (1, 4, 'WEDNESDAY', '09:00:00', '11:00:00', subs[1] if len(subs) > 1 else subs[0], fid, 'Hardware Lab 1', 'LAB'),
                (1, 4, 'WEDNESDAY', '11:15:00', '12:15:00', subs[2] if len(subs) > 2 else subs[0], fid, 'Room 301', 'LECTURE'),
                (1, 4, 'THURSDAY', '09:00:00', '10:00:00', subs[0], fid, 'Room 301', 'LECTURE'),
                (1, 4, 'THURSDAY', '10:00:00', '11:00:00', subs[1] if len(subs) > 1 else subs[0], fid, 'Room 301', 'LECTURE'),
                (1, 4, 'FRIDAY', '09:00:00', '10:00:00', subs[2] if len(subs) > 2 else subs[0], fid, 'Room 301', 'TUTORIAL'),
                (1, 4, 'FRIDAY', '10:00:00', '12:00:00', subs[0], fid, 'AI & Robotics Lab', 'LAB'),
            ]
            cur.executemany("""
                INSERT INTO class_timetable (department_id, semester, day_of_week, start_time, end_time, subject_id, faculty_id, room_no, session_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, tt)

    conn.commit()
    cur.close()
    conn.close()
    print("Database expanded with rich data: Documents, Fees, MOOCs, Quizzes, Academic Calendar, Exam Schedule & Timetable!")

if __name__ == '__main__':
    expand_db()
