from database.connection import create_connection
from utils.password import hash_password
from services.audit_service import AuditService
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


class SuperHeadService:
    """Service to handle Executive Super Head dashboard, campus analytics, department oversight, and admin management."""

    def __init__(self):
        self.audit_service = AuditService()

    def show_dashboard(self, user):
        while True:
            print("\n================================")
            print("     SUPER HEAD ERP PORTAL")
            print("================================")
            print("Executive Portal - Welcome,", user.get_full_name())
            print()
            print("1. Executive Profile")
            print("2. Campus Analytics & Overview")
            print("3. Manage Departments")
            print("4. Manage Administrators")
            print("5. System Audit Logs")
            print("6. Logout")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_profile(user)
            elif choice == "2":
                self.view_campus_analytics()
            elif choice == "3":
                self.manage_departments(user)
            elif choice == "4":
                self.manage_admins(user)
            elif choice == "5":
                self.audit_service.view_all_logs(limit=40)
            elif choice == "6":
                print("\nLogging out from Executive Portal...")
                break
            else:
                print("\nInvalid choice. Please try again.")

    def view_profile(self, user):
        query = """
            SELECT u.user_id, u.first_name, u.middle_name, u.last_name, u.email, u.phone, u.role, u.status,
                   sh.super_head_id, sh.designation, sh.date_of_birth, sh.gender, sh.blood_group,
                   sh.qualification, sh.joining_date, sh.salary, sh.emergency_contact, sh.address,
                   sh.city, sh.state, sh.pincode
            FROM users u
            LEFT JOIN super_head sh ON u.user_id = sh.user_id
            WHERE u.user_id = %s
        """
        with db_cursor() as cursor:
            cursor.execute(query, (user.user_id,))
            profile = cursor.fetchone()

        if not profile:
            print("\nSuper Head profile not found.")
            return

        full_name = " ".join(part for part in [profile["first_name"], profile["middle_name"], profile["last_name"]] if part)

        print("\n================================")
        print("       EXECUTIVE PROFILE")
        print("================================")
        print(f"Name: {full_name} | Role: {profile['role']}")
        print(f"Designation: {profile['designation'] or 'Super Head / Director'}")
        print(f"Email: {profile['email']} | Phone: {profile['phone']}")
        print(f"Qualification: {profile['qualification'] or 'N/A'} | Joining Date: {profile['joining_date'] or 'N/A'}")
        print(f"Address: {profile['address'] or 'N/A'}, {profile['city'] or ''} {profile['state'] or ''}")
        print(f"Emergency Contact: {profile['emergency_contact'] or 'N/A'}")

    def view_campus_analytics(self):
        print("\n================================")
        print("    CAMPUS ANALYTICS & STATS")
        print("================================")

        with db_cursor() as cursor:
            # Counts
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

            cursor.execute("SELECT COUNT(*) AS total FROM course")
            total_courses = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM drive")
            total_drives = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM student_application WHERE status = 'SELECTED'")
            total_placed = cursor.fetchone()["total"]

            print("\n--- High-Level Summary ---")
            print(f"Total Active Users: {total_active_users}")
            print(f"Enrolled Active Students: {total_students}")
            print(f"Active Faculty Members: {total_faculty}")
            print(f"System Administrators: {total_admins}")
            print(f"Academic Departments: {total_depts} | Courses Offered: {total_courses}")
            print(f"Placement Drives Conducted: {total_drives} | Placements Confirmed: {total_placed}")

            print("\n--- Department Breakdown ---")
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
            for ds in dept_stats:
                print(f"{ds['department_name']} ({ds['department_code']}): {ds['student_count']} Students | {ds['faculty_count']} Faculty")

    def manage_departments(self, user):
        while True:
            print("\n================================")
            print("       MANAGE DEPARTMENTS")
            print("================================")
            print("1. View All Departments")
            print("2. Add Department")
            print("3. Update Department")
            print("4. Back")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                self.view_departments()
            elif choice == "2":
                self.add_department(user)
            elif choice == "3":
                self.update_department(user)
            elif choice == "4":
                break
            else:
                print("\nInvalid choice.")

    def view_departments(self):
        print("\n================================")
        print("        ALL DEPARTMENTS")
        print("================================")

        query = "SELECT department_id, department_name, department_code FROM department ORDER BY department_id"
        with db_cursor() as cursor:
            cursor.execute(query)
            departments = cursor.fetchall()

        if not departments:
            print("\nNo departments found.")
            return

        for d in departments:
            print(f"ID: {d['department_id']} | Code: {d['department_code']} | Name: {d['department_name']}")

    def add_department(self, user):
        print("\n================================")
        print("         ADD DEPARTMENT")
        print("================================")

        dept_name = input("Department Name: ").strip()
        dept_code = input("Department Code (e.g. CSE): ").strip().upper()

        if not dept_name or not dept_code:
            print("\nDepartment name and code are required.")
            return

        with db_cursor(commit=True) as cursor:
            cursor.execute("SELECT department_id FROM department WHERE department_name = %s OR department_code = %s", (dept_name, dept_code))
            if cursor.fetchone():
                print("\nDepartment name or code already exists.")
                return

            cursor.execute("INSERT INTO department (department_name, department_code) VALUES (%s, %s)", (dept_name, dept_code))
            dept_id = cursor.lastrowid
            self.audit_service.log_action(user.user_id, 'INSERT', 'department', dept_id, f"Added department {dept_name} ({dept_code})")
            print(f"\nDepartment added successfully! (ID: {dept_id})")

    def update_department(self, user):
        print("\n================================")
        print("        UPDATE DEPARTMENT")
        print("================================")

        dept_id = input("Enter Department ID: ").strip()
        if not dept_id.isdigit():
            print("\nInvalid Department ID.")
            return

        dept_id = int(dept_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute("SELECT department_id, department_name, department_code FROM department WHERE department_id = %s", (dept_id,))
            dept = cursor.fetchone()

            if not dept:
                print("\nDepartment not found.")
                return

            print(f"Current Name: {dept['department_name']} | Code: {dept['department_code']}")
            new_name = input(f"New Name [{dept['department_name']}]: ").strip() or dept['department_name']
            new_code = input(f"New Code [{dept['department_code']}]: ").strip().upper() or dept['department_code']

            cursor.execute("UPDATE department SET department_name = %s, department_code = %s WHERE department_id = %s", (new_name, new_code, dept_id))
            self.audit_service.log_action(user.user_id, 'UPDATE', 'department', dept_id, f"Updated department to {new_name} ({new_code})")
            print("\nDepartment updated successfully.")

    def manage_admins(self, user):
        while True:
            print("\n================================")
            print("      MANAGE ADMINISTRATORS")
            print("================================")
            print("1. View All Admins")
            print("2. Add New Admin")
            print("3. Deactivate Admin")
            print("4. Back")

            choice = input("\nEnter choice: ").strip()

            if choice == "1":
                self.view_admins()
            elif choice == "2":
                self.add_admin(user)
            elif choice == "3":
                self.deactivate_admin(user)
            elif choice == "4":
                break
            else:
                print("\nInvalid choice.")

    def view_admins(self):
        print("\n================================")
        print("       ALL ADMINISTRATORS")
        print("================================")

        query = """
            SELECT a.admin_id, u.user_id, u.first_name, u.last_name, u.email, u.phone,
                   a.designation, d.department_name, a.status
            FROM admin a
            JOIN users u ON a.user_id = u.user_id
            LEFT JOIN department d ON a.department_id = d.department_id
            ORDER BY a.admin_id
        """
        with db_cursor() as cursor:
            cursor.execute(query)
            admins = cursor.fetchall()

        if not admins:
            print("\nNo administrators found.")
            return

        for a in admins:
            dept = a['department_name'] or "General Administration"
            print("\n--------------------------------")
            print(f"Admin ID: {a['admin_id']} | User ID: {a['user_id']}")
            print(f"Name: {a['first_name']} {a['last_name']} | Designation: {a['designation']}")
            print(f"Email: {a['email']} | Phone: {a['phone']}")
            print(f"Department: {dept} | Status: {a['status']}")

    def add_admin(self, user):
        print("\n================================")
        print("         ADD NEW ADMIN")
        print("================================")

        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        password = input("Password: ")
        designation = input("Designation (e.g. Dean of Academics / Admin Officer): ").strip()
        dept_id = input("Department ID (optional, press Enter for none): ").strip() or None
        dob = input("Date of Birth (YYYY-MM-DD): ").strip()
        gender = input("Gender (MALE/FEMALE/OTHER): ").strip().upper()
        qualification = input("Qualification: ").strip()
        joining_date = input("Joining Date (YYYY-MM-DD): ").strip()
        salary = input("Salary: ").strip()
        address = input("Address: ").strip()

        if not first_name or not last_name or not email or not phone or not password or not designation or not dob:
            print("\nRequired fields cannot be empty.")
            return

        try:
            salary = float(salary)
            if dept_id:
                dept_id = int(dept_id)
        except ValueError:
            print("\nInvalid numeric values entered.")
            return

        with db_cursor(commit=True) as cursor:
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                print("\nEmail already registered in system.")
                return

            pw_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (first_name, last_name, email, phone, password_hash, role, status) VALUES (%s, %s, %s, %s, %s, 'ADMIN', 'ACTIVE')",
                (first_name, last_name, email, phone, pw_hash)
            )
            new_user_id = cursor.lastrowid

            cursor.execute(
                """INSERT INTO admin (user_id, department_id, designation, date_of_birth, gender, qualification,
                                     joining_date, salary, address, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE')""",
                (new_user_id, dept_id, designation, dob, gender, qualification, joining_date, salary, address)
            )
            new_admin_id = cursor.lastrowid

            self.audit_service.log_action(user.user_id, 'INSERT', 'admin', new_admin_id, f"Created admin {first_name} {last_name}")
            print(f"\nAdministrator account created successfully! Admin ID: {new_admin_id}, User ID: {new_user_id}")

    def deactivate_admin(self, user):
        print("\n================================")
        print("       DEACTIVATE ADMIN")
        print("================================")

        admin_id = input("Enter Admin ID to deactivate: ").strip()
        if not admin_id.isdigit():
            print("\nInvalid Admin ID.")
            return

        admin_id = int(admin_id)

        with db_cursor(commit=True) as cursor:
            cursor.execute("SELECT a.admin_id, a.user_id, u.first_name, u.last_name, a.status FROM admin a JOIN users u ON a.user_id = u.user_id WHERE a.admin_id = %s", (admin_id,))
            adm = cursor.fetchone()

            if not adm:
                print("\nAdmin not found.")
                return

            if adm["status"] != "ACTIVE":
                print("\nAdmin is already inactive.")
                return

            confirm = input(f"Are you sure you want to deactivate {adm['first_name']} {adm['last_name']}? (YES/NO): ").strip().upper()
            if confirm != "YES":
                print("\nOperation cancelled.")
                return

            cursor.execute("UPDATE admin SET status = 'INACTIVE' WHERE admin_id = %s", (admin_id,))
            cursor.execute("UPDATE users SET status = 'INACTIVE' WHERE user_id = %s", (adm["user_id"],))
            self.audit_service.log_action(user.user_id, 'UPDATE', 'admin', admin_id, f"Deactivated admin {adm['first_name']} {adm['last_name']}")
            print("\nAdmin successfully deactivated.")
