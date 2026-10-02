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


class MarksService:
    """Service to handle assessment grading, CCA marks, final exams, and student report cards."""

    @staticmethod
    def calculate_grade(total_marks):
        if total_marks >= 90:
            return "O (Outstanding)", 10
        elif total_marks >= 80:
            return "A+ (Excellent)", 9
        elif total_marks >= 70:
            return "A (Very Good)", 8
        elif total_marks >= 60:
            return "B+ (Good)", 7
        elif total_marks >= 50:
            return "B (Above Average)", 6
        elif total_marks >= 40:
            return "C (Pass)", 5
        else:
            return "F (Fail)", 0

    def enter_or_update_marks(self, faculty_user):
        print("\n================================")
        print("      ENTER / UPDATE MARKS")
        print("================================")

        with db_cursor(commit=True) as cursor:
            # Find faculty ID
            cursor.execute("SELECT faculty_id FROM faculty WHERE user_id = %s", (faculty_user.user_id,))
            fac = cursor.fetchone()
            if not fac:
                print("\nFaculty record not found.")
                return
            faculty_id = fac["faculty_id"]

            cursor.execute("""
                SELECT s.subject_id, s.subject_code, s.subject_name, s.semester
                FROM faculty_subject fs
                JOIN subject s ON fs.subject_id = s.subject_id
                WHERE fs.faculty_id = %s
            """, (faculty_id,))
            subjects = cursor.fetchall()

            if not subjects:
                print("\nNo subjects assigned to you.")
                return

            print("\nAssigned Subjects:")
            for s in subjects:
                print(f"ID: {s['subject_id']} | {s['subject_code']} - {s['subject_name']} (Semester {s['semester']})")

            subject_id = input("\nEnter Subject ID: ").strip()
            if not subject_id.isdigit():
                print("\nInvalid Subject ID.")
                return
            subject_id = int(subject_id)

            academic_year = input("Academic Year (e.g. 2026-2027): ").strip()
            semester = input("Semester (1-8): ").strip()
            student_id = input("Student ID: ").strip()

            if not academic_year or not semester.isdigit() or not student_id.isdigit():
                print("\nInvalid input fields.")
                return

            semester = int(semester)
            student_id = int(student_id)

            # Check student existence
            cursor.execute("SELECT s.student_id, u.first_name, u.last_name FROM student s JOIN users u ON s.user_id = u.user_id WHERE s.student_id = %s", (student_id,))
            student = cursor.fetchone()
            if not student:
                print("\nStudent not found.")
                return

            print(f"\nEntering Marks for: {student['first_name']} {student['last_name']} (Student #{student_id})")
            try:
                cca1 = int(input("CCA 1 (Max 10): ").strip())
                cca2 = int(input("CCA 2 (Max 10): ").strip())
                cca3 = int(input("CCA 3 (Max 10): ").strip())
                midterm = int(input("Midterm Exam (Max 20): ").strip())
                final_exam = int(input("Final Exam (Max 50): ").strip())
            except ValueError:
                print("\nAll marks must be integer numbers.")
                return

            total_marks = cca1 + cca2 + cca3 + midterm + final_exam
            grade_str, gp = self.calculate_grade(total_marks)
            print(f"\nCalculated Total: {total_marks}/100 | Grade: {grade_str}")

            upsert_query = """
                INSERT INTO marks (student_id, subject_id, faculty_id, cca1, cca2, cca3, midterm, final_exam,
                                  total_marks, academic_year, semester)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    cca1 = VALUES(cca1), cca2 = VALUES(cca2), cca3 = VALUES(cca3),
                    midterm = VALUES(midterm), final_exam = VALUES(final_exam),
                    total_marks = VALUES(total_marks), faculty_id = VALUES(faculty_id),
                    updated_at = CURRENT_TIMESTAMP
            """
            cursor.execute(upsert_query, (
                student_id, subject_id, faculty_id, cca1, cca2, cca3, midterm, final_exam,
                total_marks, academic_year, semester
            ))
            print("\nMarks saved successfully!")

    def view_student_report_card(self, student_user_id):
        print("\n================================")
        print("      STUDENT REPORT CARD")
        print("================================")

        with db_cursor() as cursor:
            cursor.execute("""
                SELECT s.student_id, u.first_name, u.last_name, d.department_name
                FROM student s
                JOIN users u ON s.user_id = u.user_id
                JOIN department d ON s.department_id = d.department_id
                WHERE s.user_id = %s
            """, (student_user_id,))
            student = cursor.fetchone()

            if not student:
                print("\nStudent record not found.")
                return

            print(f"Student: {student['first_name']} {student['last_name']} (ID: {student['student_id']})")
            print(f"Department: {student['department_name']}")

            query = """
                SELECT m.marks_id, sub.subject_code, sub.subject_name, sub.credits,
                       m.cca1, m.cca2, m.cca3, m.midterm, m.final_exam, m.total_marks,
                       m.academic_year, m.semester
                FROM marks m
                JOIN subject sub ON m.subject_id = sub.subject_id
                WHERE m.student_id = %s
                ORDER BY m.academic_year DESC, m.semester, sub.subject_code
            """
            cursor.execute(query, (student["student_id"],))
            marks_list = cursor.fetchall()

            if not marks_list:
                print("\nNo assessment marks recorded yet.")
                return

            total_credits = 0
            weighted_points = 0

            for m in marks_list:
                grade, gp = self.calculate_grade(m['total_marks'])
                credits = m['credits']
                total_credits += credits
                weighted_points += (gp * credits)

                print("\n--------------------------------")
                print(f"Subject: {m['subject_name']} ({m['subject_code']}) | Credits: {credits}")
                print(f"Academic Year: {m['academic_year']} | Semester: {m['semester']}")
                print(f"CCA (1/2/3): {m['cca1']}/10, {m['cca2']}/10, {m['cca3']}/10")
                print(f"Midterm: {m['midterm']}/20 | Final Exam: {m['final_exam']}/50")
                print(f"Total: {m['total_marks']}/100 | Grade: {grade}")

            if total_credits > 0:
                sgpa = weighted_points / total_credits
                print("\n================================")
                print(f"Cumulative Credits: {total_credits} | SGPA: {sgpa:.2f}")
                print("================================")
