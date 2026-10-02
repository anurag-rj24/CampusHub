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


class AcademicService:
    """Service to handle student academic enrollments, faculty subject allocations, and curriculum schedules."""

    def enroll_student(self):
        print("\n================================")
        print("      STUDENT ENROLLMENT")
        print("================================")

        student_id = input("Student ID: ").strip()
        course_id = input("Course ID: ").strip()
        academic_year = input("Academic Year (e.g. 2026-2027): ").strip()
        semester = input("Semester (1-8): ").strip()
        enrollment_date = input("Enrollment Date (YYYY-MM-DD): ").strip()

        if not student_id.isdigit() or not course_id.isdigit() or not semester.isdigit() or not academic_year or not enrollment_date:
            print("\nInvalid enrollment input details.")
            return

        with db_cursor(commit=True) as cursor:
            # Check student exists
            cursor.execute("SELECT student_id FROM student WHERE student_id = %s", (int(student_id),))
            if not cursor.fetchone():
                print("\nStudent not found.")
                return

            # Check course exists
            cursor.execute("SELECT course_id FROM course WHERE course_id = %s", (int(course_id),))
            if not cursor.fetchone():
                print("\nCourse not found.")
                return

            query = """
                INSERT INTO student_enrollment (student_id, course_id, academic_year, semester, enrollment_date, status)
                VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
                ON DUPLICATE KEY UPDATE status = 'ACTIVE'
            """
            cursor.execute(query, (int(student_id), int(course_id), academic_year, int(semester), enrollment_date))
            print("\nStudent enrolled in course successfully!")
            print("Enrollment ID:", cursor.lastrowid)

    def view_student_enrollments(self, student_user_id):
        print("\n================================")
        print("     MY COURSE ENROLLMENTS")
        print("================================")

        query = """
            SELECT se.enrollment_id, c.course_name, c.course_code, c.degree_level,
                   se.academic_year, se.semester, se.enrollment_date, se.status, se.completion_date
            FROM student_enrollment se
            JOIN student s ON se.student_id = s.student_id
            JOIN course c ON se.course_id = c.course_id
            WHERE s.user_id = %s
            ORDER BY se.academic_year DESC, se.semester DESC
        """
        with db_cursor() as cursor:
            cursor.execute(query, (student_user_id,))
            enrollments = cursor.fetchall()

        if not enrollments:
            print("\nNo course enrollments found.")
            return

        for e in enrollments:
            print("\n--------------------------------")
            print(f"Course: {e['course_name']} ({e['course_code']}) | Degree: {e['degree_level']}")
            print(f"Academic Year: {e['academic_year']} | Semester: {e['semester']}")
            print(f"Enrolled Date: {e['enrollment_date']} | Status: {e['status']}")
            if e['completion_date']:
                print(f"Completion Date: {e['completion_date']}")

    def assign_subject_to_faculty(self):
        print("\n================================")
        print("     ASSIGN FACULTY SUBJECT")
        print("================================")

        faculty_id = input("Faculty ID: ").strip()
        subject_id = input("Subject ID: ").strip()

        if not faculty_id.isdigit() or not subject_id.isdigit():
            print("\nInvalid IDs entered.")
            return

        with db_cursor(commit=True) as cursor:
            # Check faculty
            cursor.execute("SELECT faculty_id FROM faculty WHERE faculty_id = %s", (int(faculty_id),))
            if not cursor.fetchone():
                print("\nFaculty not found.")
                return

            # Check subject
            cursor.execute("SELECT subject_id FROM subject WHERE subject_id = %s", (int(subject_id),))
            if not cursor.fetchone():
                print("\nSubject not found.")
                return

            query = "INSERT INTO faculty_subject (faculty_id, subject_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE assigned_at = CURRENT_TIMESTAMP"
            cursor.execute(query, (int(faculty_id), int(subject_id)))
            print("\nSubject assigned to faculty successfully!")

    def view_faculty_assigned_subjects(self, faculty_user_id):
        print("\n================================")
        print("       ASSIGNED SUBJECTS")
        print("================================")

        query = """
            SELECT s.subject_id, s.subject_code, s.subject_name, s.credits, s.semester, s.subject_type,
                   d.department_name, fs.assigned_at
            FROM faculty_subject fs
            JOIN faculty f ON fs.faculty_id = f.faculty_id
            JOIN subject s ON fs.subject_id = s.subject_id
            JOIN department d ON s.department_id = d.department_id
            WHERE f.user_id = %s
            ORDER BY s.semester, s.subject_code
        """
        with db_cursor() as cursor:
            cursor.execute(query, (faculty_user_id,))
            subjects = cursor.fetchall()

        if not subjects:
            print("\nNo subjects assigned.")
            return

        for s in subjects:
            print("\n--------------------------------")
            print(f"Subject: {s['subject_name']} ({s['subject_code']}) | ID: {s['subject_id']}")
            print(f"Department: {s['department_name']} | Semester: {s['semester']}")
            print(f"Credits: {s['credits']} | Type: {s['subject_type']}")
            print(f"Assigned At: {s['assigned_at']}")
