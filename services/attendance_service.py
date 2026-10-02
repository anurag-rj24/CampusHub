from database.connection import create_connection
from contextlib import contextmanager


@contextmanager
def db_cursor(dictionary=True, commit=False):
    """Context manager to handle DB connections and boilerplate."""
    connection = create_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception as error:
        if commit:
            connection.rollback()
        print(f"\nDatabase Error: {error}")
    finally:
        cursor.close()
        connection.close()


class AttendanceService:
    """Service to handle class sessions, attendance marking, student reports, and eligibility calculation."""

    def create_session(self, faculty_id, subject_id, session_date, start_time, end_time, room_no="Room 101", session_type="LECTURE"):
        query = """
            INSERT INTO class_session (subject_id, faculty_id, session_date, start_time, end_time, room_no, session_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        with db_cursor(commit=True) as cursor:
            cursor.execute(query, (subject_id, faculty_id, session_date, start_time, end_time, room_no, session_type))
            return cursor.lastrowid

    def mark_attendance_for_session(self, faculty_user):
        print("\n================================")
        print("        MARK ATTENDANCE")
        print("================================")

        with db_cursor() as cursor:
            # Find faculty ID
            cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (faculty_user.user_id,))
            fac = cursor.fetchone()
            if not fac:
                print("\nFaculty record not found.")
                return
            faculty_id = fac["faculty_id"]

            # Fetch assigned subjects
            cursor.execute("""
                SELECT s.subject_id, s.subject_code, s.subject_name
                FROM faculty_subject fs
                JOIN subject s ON fs.subject_id = s.subject_id
                WHERE fs.faculty_id = %s
            """, (faculty_id,))
            subjects = cursor.fetchall()

            if not subjects:
                print("\nNo subjects assigned to your faculty account.")
                return

            print("\nAssigned Subjects:")
            for s in subjects:
                print(f"ID: {s['subject_id']} | {s['subject_code']} - {s['subject_name']}")

            subject_id = input("\nEnter Subject ID: ").strip()
            if not subject_id.isdigit():
                print("\nInvalid Subject ID.")
                return
            subject_id = int(subject_id)

            session_date = input("Session Date (YYYY-MM-DD): ").strip()
            start_time = input("Start Time (HH:MM, e.g. 09:00): ").strip()
            end_time = input("End Time (HH:MM, e.g. 10:00): ").strip()
            room_no = input("Room Number (optional, default 101): ").strip() or "101"

            print("\nSession Types: 1. LECTURE, 2. LAB, 3. TUTORIAL")
            st_choice = input("Select Type (1-3, default 1): ").strip()
            st_map = {"1": "LECTURE", "2": "LAB", "3": "TUTORIAL"}
            session_type = st_map.get(st_choice, "LECTURE")

            # Create session
            session_id = self.create_session(faculty_id, subject_id, session_date, start_time, end_time, room_no, session_type)
            print(f"\nClass session created! (Session ID: {session_id})")

            # Fetch students in this subject's department or enrolled
            cursor.execute("""
                SELECT s.student_id, u.first_name, u.last_name, u.email
                FROM student s
                JOIN users u ON s.user_id = u.user_id
                JOIN subject sub ON s.department_id = sub.department_id
                WHERE sub.subject_id = %s AND s.student_status = 'ACTIVE'
                ORDER BY s.student_id
            """, (subject_id,))
            students = cursor.fetchall()

            if not students:
                print("\nNo active students found in this department/subject.")
                return

            print(f"\nMarking attendance for {len(students)} students:")
            print("Enter 'P' for Present, 'A' for Absent (Default is P):")

            attendance_records = []
            for student in students:
                name = f"{student['first_name']} {student['last_name']}"
                att_input = input(f"Student #{student['student_id']} - {name} [P/A]: ").strip().upper()
                status = "ABSENT" if att_input == "A" else "PRESENT"
                remarks = input("Remarks (optional): ").strip() or None if status == "ABSENT" else None
                attendance_records.append((student['student_id'], session_id, status, remarks))

        with db_cursor(commit=True) as cursor:
            insert_query = """
                INSERT INTO attendance (student_id, session_id, status, remarks)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE status = VALUES(status), remarks = VALUES(remarks)
            """
            cursor.executemany(insert_query, attendance_records)
            print("\nAttendance recorded successfully for all students!")

    def view_student_attendance(self, student_user_id):
        print("\n================================")
        print("       ATTENDANCE REPORT")
        print("================================")

        query = """
            SELECT s.student_id FROM student s WHERE s.user_id = %s
        """
        with db_cursor() as cursor:
            cursor.execute(query, (student_user_id,))
            student = cursor.fetchone()

            if not student:
                print("\nStudent record not found.")
                return

            student_id = student["student_id"]

            stats_query = """
                SELECT sub.subject_code, sub.subject_name,
                       COUNT(a.attendance_id) AS total_sessions,
                       SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS present_count,
                       SUM(CASE WHEN a.status = 'ABSENT' THEN 1 ELSE 0 END) AS absent_count
                FROM attendance a
                JOIN class_session cs ON a.session_id = cs.session_id
                JOIN subject sub ON cs.subject_id = sub.subject_id
                WHERE a.student_id = %s
                GROUP BY sub.subject_id, sub.subject_code, sub.subject_name
            """
            cursor.execute(stats_query, (student_id,))
            records = cursor.fetchall()

            if not records:
                print("\nNo attendance records found.")
                return

            overall_total = 0
            overall_present = 0

            for rec in records:
                total = rec["total_sessions"]
                present = rec["present_count"] or 0
                absent = rec["absent_count"] or 0
                pct = (present / total * 100) if total > 0 else 0.0
                overall_total += total
                overall_present += present

                status_flag = "ELIGIBLE" if pct >= 75.0 else "SHORTAGE (<75%)"
                print("\n--------------------------------")
                print(f"Subject: {rec['subject_name']} ({rec['subject_code']})")
                print(f"Total Classes: {total} | Present: {present} | Absent: {absent}")
                print(f"Attendance: {pct:.2f}% | Status: {status_flag}")

            overall_pct = (overall_present / overall_total * 100) if overall_total > 0 else 0.0
            print("\n================================")
            print(f"Overall Attendance: {overall_pct:.2f}% ({overall_present}/{overall_total} classes)")
            print("================================")
