from services.auth_service import AuthService
from services.student_service import StudentService
from services.faculty_service import FacultyService
from services.admin_service import AdminService
from services.super_head_service import SuperHeadService
from services.audit_service import AuditService


def main():
    print("================================")
    print("       CAMPUS HUB LOGIN")
    print("================================")

    email = input("Enter email: ")
    password = input("Enter password: ")

    auth_service = AuthService()
    user = auth_service.login(email, password)

    if user is None:
        print("\nInvalid email or password.")
        return

    # Log successful login
    AuditService.log_action(user.user_id, 'LOGIN', 'users', user.user_id, f"User logged in as {user.role}")

    print("\nLogin successful!")
    print("Welcome,", user.get_full_name())
    print("Role:", user.role)

    if user.role == "STUDENT":
        student_service = StudentService()
        student_service.show_dashboard(user)

    elif user.role == "FACULTY":
        faculty_service = FacultyService()
        faculty_service.show_dashboard(user)

    elif user.role == "ADMIN":
        admin_service = AdminService()
        admin_service.show_dashboard(user)

    elif user.role == "SUPER_HEAD":
        super_head_service = SuperHeadService()
        super_head_service.show_dashboard(user)

    else:
        print("Unknown user role.")

    # Log logout on exit
    AuditService.log_action(user.user_id, 'LOGOUT', 'users', user.user_id, "User session ended")


if __name__ == "__main__":
    main()