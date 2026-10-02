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


class PlacementService:
    """Service to handle student placement drives, job applications, criteria eligibility, and hiring news."""

    def view_open_drives(self, student_user=None):
        print("\n================================")
        print("     ACTIVE PLACEMENT DRIVES")
        print("================================")

        query = """
            SELECT d.drive_id, c.company_name, d.drive_title, d.job_role, d.job_location,
                   d.package_in_lpa, d.minimum_cgpa, d.minimum_10th_percentage, d.minimum_12th_percentage,
                   d.maximum_backlogs, d.eligible_degree, d.eligible_branch, d.application_deadline,
                   d.drive_status
            FROM drive d
            JOIN company c ON d.company_id = c.company_id
            WHERE d.drive_status IN ('OPEN', 'UPCOMING')
            ORDER BY d.drive_date ASC, d.drive_id DESC
        """
        with db_cursor() as cursor:
            cursor.execute(query)
            drives = cursor.fetchall()

        if not drives:
            print("\nNo open placement drives at this moment.")
            return

        for d in drives:
            print("\n--------------------------------")
            print(f"Drive ID: {d['drive_id']} | Company: {d['company_name']}")
            print(f"Title: {d['drive_title']} | Role: {d['job_role']}")
            print(f"Location: {d['job_location']} | Package: {d['package_in_lpa']} LPA")
            print(f"Eligibility: Min CGPA: {d['minimum_cgpa'] or 'None'} | Max Backlogs: {d['maximum_backlogs']}")
            print(f"Degree: {d['eligible_degree'] or 'All'} | Branch: {d['eligible_branch'] or 'All'}")
            print(f"Deadline: {d['application_deadline'] or 'Open'} | Status: {d['drive_status']}")

    def apply_for_drive(self, student_user):
        print("\n================================")
        print("   APPLY FOR PLACEMENT DRIVE")
        print("================================")

        with db_cursor(commit=True) as cursor:
            # Fetch student ID
            cursor.execute("SELECT student_id, student_status FROM student WHERE user_id = %s", (student_user.user_id,))
            student = cursor.fetchone()
            if not student:
                print("\nStudent record not found.")
                return

            if student["student_status"] != "ACTIVE":
                print(f"\nCannot apply. Student status is {student['student_status']}.")
                return

            student_id = student["student_id"]

            drive_id = input("\nEnter Placement Drive ID: ").strip()
            if not drive_id.isdigit():
                print("\nInvalid Drive ID.")
                return
            drive_id = int(drive_id)

            # Check drive validity
            cursor.execute("""
                SELECT d.drive_id, d.drive_title, d.drive_status, c.company_name
                FROM drive d
                JOIN company c ON d.company_id = c.company_id
                WHERE d.drive_id = %s
            """, (drive_id,))
            drive = cursor.fetchone()

            if not drive:
                print("\nDrive not found.")
                return

            if drive["drive_status"] != "OPEN":
                print(f"\nThis drive is currently {drive['drive_status']} and not accepting applications.")
                return

            # Check already applied
            cursor.execute("SELECT application_id, status FROM student_application WHERE student_id = %s AND drive_id = %s", (student_id, drive_id))
            existing = cursor.fetchone()
            if existing:
                print(f"\nYou have already applied for this drive! Current Status: {existing['status']}.")
                return

            # Insert application
            query = "INSERT INTO student_application (student_id, drive_id, status) VALUES (%s, %s, 'APPLIED')"
            cursor.execute(query, (student_id, drive_id))
            print("\n================================")
            print(f"Applied successfully for {drive['drive_title']} at {drive['company_name']}!")
            print("Application ID:", cursor.lastrowid)
            print("Status: APPLIED")
            print("================================")

    def view_my_applications(self, student_user):
        print("\n================================")
        print("     MY PLACEMENT APPLICATIONS")
        print("================================")

        query = """
            SELECT sa.application_id, c.company_name, d.drive_title, d.job_role,
                   d.package_in_lpa, sa.status, sa.remarks, sa.applied_at
            FROM student_application sa
            JOIN student s ON sa.student_id = s.student_id
            JOIN drive d ON sa.drive_id = d.drive_id
            JOIN company c ON d.company_id = c.company_id
            WHERE s.user_id = %s
            ORDER BY sa.application_id DESC
        """
        with db_cursor() as cursor:
            cursor.execute(query, (student_user.user_id,))
            apps = cursor.fetchall()

        if not apps:
            print("\nYou have not applied to any placement drives yet.")
            return

        for a in apps:
            print("\n--------------------------------")
            print(f"Application ID: {a['application_id']} | Company: {a['company_name']}")
            print(f"Drive: {a['drive_title']} | Role: {a['job_role']} ({a['package_in_lpa']} LPA)")
            print(f"Status: {a['status']} | Applied At: {a['applied_at']}")
            if a['remarks']:
                print(f"Remarks: {a['remarks']}")
