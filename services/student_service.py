from database.connection import create_connection
from services.attendance_service import AttendanceService
from services.marks_service import MarksService
from services.notice_service import NoticeService
from services.leave_service import LeaveService
from services.placement_service import PlacementService
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


class StudentService:
    """Service to handle all student portal interactions, academics, assessments, attendance, and placements."""

    def __init__(self):
        self.attendance_service = AttendanceService()
        self.marks_service = MarksService()
        self.notice_service = NoticeService()
        self.leave_service = LeaveService()
        self.placement_service = PlacementService()
        self.academic_service = AcademicService()

    def show_dashboard(self, user):
        while True:
            print("\n================================")
            print("       STUDENT DASHBOARD")
            print("================================")
            print("Welcome,", user.get_full_name())
            print()
            print("1. View Profile")
            print("2. View Course Enrollments")
            print("3. View Attendance Report")
            print("4. View Assessment Marks & Report Card")
            print("5. View Campus Notices")
            print("6. Browse Placement Drives")
            print("7. Apply for Placement Drive")
            print("8. View My Placement Applications")
            print("9. Apply for Leave")
            print("10. View My Leave Requests")
            print("11. Logout")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_profile(user)
            elif choice == "2":
                self.academic_service.view_student_enrollments(user.user_id)
            elif choice == "3":
                self.attendance_service.view_student_attendance(user.user_id)
            elif choice == "4":
                self.marks_service.view_student_report_card(user.user_id)
            elif choice == "5":
                self.notice_service.view_notices_for_user(user)
            elif choice == "6":
                self.placement_service.view_open_drives(user)
            elif choice == "7":
                self.placement_service.apply_for_drive(user)
            elif choice == "8":
                self.placement_service.view_my_applications(user)
            elif choice == "9":
                self.leave_service.apply_leave(user)
            elif choice == "10":
                self.leave_service.view_my_leaves(user)
            elif choice == "11":
                print("\nLogging out from Student Portal...")
                break
            else:
                print("\nInvalid choice. Please try again.")

    def view_profile(self, user):
        query = """
            SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.phone, u.role, u.status,
                   s.student_id, s.date_of_birth, s.gender, s.blood_group, s.father_name, s.mother_name,
                   s.previous_qualification, s.previous_percentage, s.admission_date, s.address,
                   s.city, s.state, s.pincode, s.emergency_contact, s.student_status,
                   d.department_name, d.department_code
            FROM users u
            INNER JOIN student s ON u.user_id = s.user_id
            INNER JOIN department d ON s.department_id = d.department_id
            WHERE u.user_id = %s
        """
        with db_cursor() as cursor:
            cursor.execute(query, (user.user_id,))
            student_data = cursor.fetchone()

        if student_data is None:
            print("\nStudent profile not found.")
            return

        print("\n================================")
        print("          STUDENT PROFILE")
        print("================================")
        full_name = " ".join([student_data["first_name"], student_data["middle_name"] or "", student_data["last_name"]]).split()

        print("\n--- Account Information ---")
        print("User ID:", student_data["user_id"])
        print("Name:", " ".join(full_name))
        print("Email:", student_data["email"])
        print("Phone:", student_data["phone"])
        print("Role:", student_data["role"])
        print("Account Status:", student_data["status"])

        print("\n--- Academic Information ---")
        print("Student ID:", student_data["student_id"])
        print("Department:", student_data["department_name"], f"({student_data['department_code']})")
        print("Admission Date:", student_data["admission_date"])
        print("Previous Qualification:", student_data["previous_qualification"])
        print("Previous Percentage:", student_data["previous_percentage"])
        print("Student Status:", student_data["student_status"])

        print("\n--- Personal Information ---")
        print("Date of Birth:", student_data["date_of_birth"])
        print("Gender:", student_data["gender"])
        print("Blood Group:", student_data["blood_group"])
        print("Parents:", student_data["father_name"], "(Father),", student_data["mother_name"], "(Mother)")

        print("\n--- Address Information ---")
        print("Address:", student_data["address"])
        print(f"Location: {student_data['city']}, {student_data['state']} - {student_data['pincode']}")
        print("Emergency Contact:", student_data["emergency_contact"])