from services.auth_service import AuthService
from services.student_service import StudentService
from services.faculty_service import FacultyService
from services.admin_service import AdminService


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

        admin_service = AdminService()
        admin_service.show_dashboard(user)

    else:
        print("Unknown user role.")


if __name__ == "__main__":
    main()