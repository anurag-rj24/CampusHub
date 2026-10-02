from database.connection import create_connection
from services.attendance_service import AttendanceService
from services.marks_service import MarksService
from services.notice_service import NoticeService
from services.leave_service import LeaveService
from services.academic_service import AcademicService
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


class FacultyService:
    """Service to handle Faculty ERP dashboard, class teaching, attendance marking, grading, and leaves."""

    def __init__(self):
        self.attendance_service = AttendanceService()
        self.marks_service = MarksService()
        self.notice_service = NoticeService()
        self.leave_service = LeaveService()
        self.academic_service = AcademicService()

    def show_dashboard(self, user):
        while True:
            print("\n================================")
            print("       FACULTY DASHBOARD")
            print("================================")
            print("Welcome,", user.get_full_name())
            print()
            print("1. View Profile")
            print("2. View Assigned Subjects")
            print("3. Mark Class Attendance")
            print("4. Enter / Update Student Marks")
            print("5. View Campus Notices")
            print("6. Apply for Leave")
            print("7. View My Leave Requests")
            print("8. Logout")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_profile(user)
            elif choice == "2":
                self.academic_service.view_faculty_assigned_subjects(user.user_id)
            elif choice == "3":
                self.attendance_service.mark_attendance_for_session(user)
            elif choice == "4":
                self.marks_service.enter_or_update_marks(user)
            elif choice == "5":
                self.notice_service.view_notices_for_user(user)
            elif choice == "6":
                self.leave_service.apply_leave(user)
            elif choice == "7":
                self.leave_service.view_my_leaves(user)
            elif choice == "8":
                print("\nLogging out from Faculty Portal...")
                break
            else:
                print("\nInvalid choice. Please try again.")

    def view_profile(self, user):
        query = """
            SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.phone, u.role, u.status,
                   f.faculty_id, f.department_id, f.designation, f.date_of_birth, f.gender, f.blood_group,
                   f.father_name, f.mother_name, f.address, f.city, f.state, f.pincode, f.qualification,
                   f.specialization, f.joining_date, f.salary, f.employment_type, f.emergency_contact,
                   f.status AS faculty_status, d.department_name, d.department_code
            FROM users u
            INNER JOIN faculty f ON u.user_id = f.user_id
            LEFT JOIN department d ON f.department_id = d.department_id
            WHERE u.user_id = %s
        """
        with db_cursor() as cursor:
            cursor.execute(query, (user.user_id,))
            fac = cursor.fetchone()

        if not fac:
            print("\nFaculty profile not found.")
            return

        full_name = " ".join([fac["first_name"], fac["middle_name"] or "", fac["last_name"]]).split()

        print("\n================================")
        print("         FACULTY PROFILE")
        print("================================")
        print("\n--- Account Information ---")
        print("User ID:", fac["user_id"])
        print("Name:", " ".join(full_name))
        print("Email:", fac["email"])
        print("Phone:", fac["phone"])
        print("Role:", fac["role"])
        print("Account Status:", fac["status"])

        print("\n--- Academic Information ---")
        print("Faculty ID:", fac["faculty_id"])
        print("Department:", fac["department_name"], f"({fac['department_code']})")
        print("Designation:", fac["designation"])
        print("Qualification:", fac["qualification"])
        print("Specialization:", fac["specialization"] or "N/A")
        print("Joining Date:", fac["joining_date"])
        print("Employment Type:", fac["employment_type"])

        print("\n--- Personal Information ---")
        print("Date of Birth:", fac["date_of_birth"])
        print("Gender:", fac["gender"])
        print("Blood Group:", fac["blood_group"])
        print("Parents:", fac["father_name"] or "N/A", "(Father),", fac["mother_name"] or "N/A", "(Mother)")

        print("\n--- Address Information ---")
        print("Address:", fac["address"])
        print(f"Location: {fac['city']}, {fac['state']} - {fac['pincode']}")
        print("Emergency Contact:", fac["emergency_contact"])
