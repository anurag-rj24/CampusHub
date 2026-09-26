from database.connection import create_connection
from utils.password import hash_password


class AdminService:

    def show_dashboard(self, user):
        while True:
            print("\n================================")
            print("         ADMIN DASHBOARD")
            print("================================")
            print("Welcome,", user.get_full_name())
            print()
            print("1. View Profile")
            print("2. Manage Students")
            print("3. Manage Faculty")
            print("4. Manage Courses")
            print("5. Manage Subjects")
            print("6. Manage Notices")
            print("7. Manage Leave Requests")
            print("8. Manage Placement")
            print("9. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_profile(user)

            elif choice == "2":
                self.manage_students(user)

            elif choice == "3":
                self.manage_faculty(user)

            elif choice == "4":
                self.manage_courses(user)

            elif choice == "5":
                self.manage_subjects(user)

            elif choice == "6":
                self.manage_notices(user)

            elif choice == "7":
                self.manage_leave_requests(user)

            elif choice == "8":
                self.manage_placement(user)

            elif choice == "9":
                print("\nLogging out...")
                break

            else:
                print("\nInvalid choice. Please try again.")

    def view_profile(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                u.user_id,
                u.first_name,
                u.middle_name,
                u.last_name,
                u.email,
                u.phone,
                u.role,
                u.status,

                a.admin_id,
                a.department_id,
                a.designation,
                a.date_of_birth,
                a.gender,
                a.blood_group,
                a.father_name,
                a.mother_name,
                a.address,
                a.city,
                a.state,
                a.pincode,
                a.qualification,
                a.joining_date,
                a.salary,
                a.employment_type,
                a.emergency_contact,
                a.status AS admin_status,

                d.department_name,
                d.department_code

            FROM users u

            INNER JOIN admin a
                ON u.user_id = a.user_id

            LEFT JOIN department d
                ON a.department_id = d.department_id

            WHERE u.user_id = %s
        """

        cursor.execute(query, (user.user_id,))

        admin_data = cursor.fetchone()

        if admin_data is None:
            print("\nAdmin profile not found.")

            cursor.close()
            connection.close()
            return

        print("\n================================")
        print("          ADMIN PROFILE")
        print("================================")

        print("\n--- Account Information ---")
        print("User ID:", admin_data["user_id"])

        full_name = (
            admin_data["first_name"]
            + " "
            + (admin_data["middle_name"] or "")
            + " "
            + admin_data["last_name"]
        )

        print("Name:", " ".join(full_name.split()))
        print("Email:", admin_data["email"])
        print("Phone:", admin_data["phone"])
        print("Role:", admin_data["role"])
        print("Account Status:", admin_data["status"])

        print("\n--- Administrative Information ---")
        print("Admin ID:", admin_data["admin_id"])
        print("Designation:", admin_data["designation"])
        print("Department:", admin_data["department_name"])
        print("Department Code:", admin_data["department_code"])
        print("Qualification:", admin_data["qualification"])
        print("Joining Date:", admin_data["joining_date"])
        print("Employment Type:", admin_data["employment_type"])
        print("Salary:", admin_data["salary"])
        print("Admin Status:", admin_data["admin_status"])

        print("\n--- Personal Information ---")
        print("Date of Birth:", admin_data["date_of_birth"])
        print("Gender:", admin_data["gender"])
        print("Blood Group:", admin_data["blood_group"])
        print("Father Name:", admin_data["father_name"])
        print("Mother Name:", admin_data["mother_name"])

        print("\n--- Address Information ---")
        print("Address:", admin_data["address"])
        print("City:", admin_data["city"])
        print("State:", admin_data["state"])
        print("Pincode:", admin_data["pincode"])
        print("Emergency Contact:", admin_data["emergency_contact"])

        cursor.close()
        connection.close()

    def manage_students(self, user):

        while True:

            print("\n================================")
            print("         MANAGE STUDENTS")
            print("================================")

            print("1. View All Students")
            print("2. View Student Details")
            print("3. Add Student")
            print("4. Update Student")
            print("5. Deactivate Student")
            print("6. Back")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_all_students()

            elif choice == "2":
                self.view_student_details()

            elif choice == "3":
               self.add_student()

            elif choice == "4":
                 self.update_student()

            elif choice == "5":
                self.deactivate_student()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice. Please try again.")


    def view_all_students(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                s.student_id,
                u.user_id,
                u.first_name,
                u.middle_name,
                u.last_name,
                u.email,
                u.phone,
                d.department_name,
                d.department_code,
                s.admission_date,
                s.student_status
            FROM student s
            INNER JOIN users u
                ON s.user_id = u.user_id
            INNER JOIN department d
                ON s.department_id = d.department_id
            ORDER BY s.student_id
        """

        cursor.execute(query)

        students = cursor.fetchall()

        if not students:
            print("\nNo students found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("          ALL STUDENTS")
        print("================================")

        for student in students:

            full_name = (
                student["first_name"]
                + " "
                + (student["middle_name"] or "")
                + " "
                + student["last_name"]
            )

            print("\n--------------------------------")
            print("Student ID:", student["student_id"])
            print("User ID:", student["user_id"])
            print("Name:", " ".join(full_name.split()))
            print("Email:", student["email"])
            print("Phone:", student["phone"])
            print("Department:", student["department_name"])
            print("Department Code:", student["department_code"])
            print("Admission Date:", student["admission_date"])
            print("Status:", student["student_status"])

        cursor.close()
        connection.close()


    def view_student_details(self):

        student_id = input("\nEnter Student ID: ")

        if not student_id.isdigit():
            print("\nInvalid Student ID.")
            return

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                s.student_id,
                u.user_id,
                u.first_name,
                u.middle_name,
                u.last_name,
                u.email,
                u.phone,
                u.role,
                u.status AS account_status,

                s.date_of_birth,
                s.gender,
                s.blood_group,
                s.father_name,
                s.mother_name,
                s.previous_qualification,
                s.previous_percentage,
                s.admission_date,
                s.address,
                s.city,
                s.state,
                s.pincode,
                s.emergency_contact,
                s.student_status,

                d.department_name,
                d.department_code

            FROM student s

            INNER JOIN users u
                ON s.user_id = u.user_id

            INNER JOIN department d
                ON s.department_id = d.department_id

            WHERE s.student_id = %s
        """

        cursor.execute(query, (int(student_id),))

        student = cursor.fetchone()

        if student is None:
            print("\nStudent not found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("         STUDENT DETAILS")
        print("================================")

        full_name = (
            student["first_name"]
            + " "
            + (student["middle_name"] or "")
            + " "
            + student["last_name"]
        )

        print("\n--- Account Information ---")
        print("User ID:", student["user_id"])
        print("Student ID:", student["student_id"])
        print("Name:", " ".join(full_name.split()))
        print("Email:", student["email"])
        print("Phone:", student["phone"])
        print("Account Status:", student["account_status"])

        print("\n--- Academic Information ---")
        print("Department:", student["department_name"])
        print("Department Code:", student["department_code"])
        print("Previous Qualification:", student["previous_qualification"])
        print("Previous Percentage:", student["previous_percentage"])
        print("Admission Date:", student["admission_date"])
        print("Student Status:", student["student_status"])

        print("\n--- Personal Information ---")
        print("Date of Birth:", student["date_of_birth"])
        print("Gender:", student["gender"])
        print("Blood Group:", student["blood_group"])
        print("Father Name:", student["father_name"])
        print("Mother Name:", student["mother_name"])

        print("\n--- Address Information ---")
        print("Address:", student["address"])
        print("City:", student["city"])
        print("State:", student["state"])
        print("Pincode:", student["pincode"])
        print("Emergency Contact:", student["emergency_contact"])

        cursor.close()
        connection.close()

    def add_student(self):

        print("\n================================")
        print("           ADD STUDENT")
        print("================================")

        print("\n--- Account Information ---")

        first_name = input("First Name: ").strip()
        middle_name = input("Middle Name (optional): ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        password = input("Password: ")

        print("\n--- Personal Information ---")

        date_of_birth = input("Date of Birth (YYYY-MM-DD): ").strip()
        gender = input("Gender (MALE/FEMALE/OTHER): ").strip().upper()
        blood_group = input(
            "Blood Group (A+/A-/B+/B-/AB+/AB-/O+/O-): "
        ).strip().upper()

        father_name = input("Father Name: ").strip()
        mother_name = input("Mother Name: ").strip()

        print("\n--- Academic Information ---")

        previous_qualification = input(
            "Previous Qualification: "
        ).strip()

        previous_percentage = input(
            "Previous Percentage (optional): "
        ).strip()

        admission_date = input(
            "Admission Date (YYYY-MM-DD): "
        ).strip()

        department_id = input("Department ID: ").strip()

        print("\n--- Address Information ---")

        address = input("Address: ").strip()
        city = input("City: ").strip()
        state = input("State: ").strip()
        pincode = input("Pincode: ").strip()
        emergency_contact = input(
            "Emergency Contact: "
        ).strip()

        if not first_name or not last_name:
            print("\nFirst name and last name are required.")
            return

        if not email or not phone or not password:
            print("\nEmail, phone and password are required.")
            return

        if gender not in ("MALE", "FEMALE", "OTHER"):
            print("\nInvalid gender.")
            return

        valid_blood_groups = (
            "A+", "A-",
            "B+", "B-",
            "AB+", "AB-",
            "O+", "O-"
        )

        if blood_group and blood_group not in valid_blood_groups:
            print("\nInvalid blood group.")
            return

        if not department_id.isdigit():
            print("\nInvalid department ID.")
            return

        if previous_percentage:
            try:
                previous_percentage = float(previous_percentage)
            except ValueError:
                print("\nInvalid previous percentage.")
                return
        else:
            previous_percentage = None

        connection = create_connection()
        cursor = connection.cursor()

        try:

            check_query = """
                SELECT user_id
                FROM users
                WHERE email = %s
            """

            cursor.execute(check_query, (email,))

            existing_user = cursor.fetchone()

            if existing_user is not None:
                print("\nEmail already exists.")

                connection.rollback()
                return

            password_hash = hash_password(password)

            user_query = """
                INSERT INTO users (
                    first_name,
                    middle_name,
                    last_name,
                    email,
                    phone,
                    password_hash,
                    role,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, 'STUDENT', 'ACTIVE'
                )
            """

            cursor.execute(
                user_query,
                (
                    first_name,
                    middle_name if middle_name else None,
                    last_name,
                    email,
                    phone,
                    password_hash
                )
            )

            user_id = cursor.lastrowid

            student_query = """
                INSERT INTO student (
                    user_id,
                    date_of_birth,
                    gender,
                    blood_group,
                    father_name,
                    mother_name,
                    previous_qualification,
                    previous_percentage,
                    admission_date,
                    department_id,
                    address,
                    city,
                    state,
                    pincode,
                    emergency_contact,
                    student_status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, 'ACTIVE'
                )
            """

            cursor.execute(
                student_query,
                (
                    user_id,
                    date_of_birth,
                    gender,
                    blood_group if blood_group else None,
                    father_name,
                    mother_name,
                    previous_qualification,
                    previous_percentage,
                    admission_date,
                    int(department_id),
                    address,
                    city,
                    state,
                    pincode,
                    emergency_contact
                )
            )

            student_id = cursor.lastrowid

            connection.commit()

            print("\nStudent added successfully.")
            print("User ID:", user_id)
            print("Student ID:", student_id)

        except Exception as error:

            connection.rollback()

            print("\nFailed to add student.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def update_student(self):

        print("\n================================")
        print("         UPDATE STUDENT")
        print("================================")

        student_id = input("Enter Student ID: ").strip()

        if not student_id.isdigit():
            print("\nInvalid Student ID.")
            return

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    s.student_id,
                    u.user_id,
                    u.first_name,
                    u.middle_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    s.date_of_birth,
                    s.gender,
                    s.blood_group,
                    s.father_name,
                    s.mother_name,
                    s.previous_qualification,
                    s.previous_percentage,
                    s.admission_date,
                    s.department_id,
                    s.address,
                    s.city,
                    s.state,
                    s.pincode,
                    s.emergency_contact
                FROM student s
                INNER JOIN users u
                    ON s.user_id = u.user_id
                WHERE s.student_id = %s
            """

            cursor.execute(query, (int(student_id),))

            student = cursor.fetchone()

            if student is None:
                print("\nStudent not found.")
                return

            print("\nCurrent Student Information")
            print("---------------------------")
            print(
                "Name:",
                student["first_name"],
                student["middle_name"] or "",
                student["last_name"]
            )
            print("Email:", student["email"])
            print("Phone:", student["phone"])
            print("Department ID:", student["department_id"])
            print("City:", student["city"])

            print("\nEnter new values.")
            print("Press ENTER to keep the current value.")

            first_name = input(
                f"First Name [{student['first_name']}]: "
            ).strip()

            last_name = input(
                f"Last Name [{student['last_name']}]: "
            ).strip()

            phone = input(
                f"Phone [{student['phone']}]: "
            ).strip()

            city = input(
                f"City [{student['city'] or ''}]: "
            ).strip()

            state = input(
                f"State [{student['state'] or ''}]: "
            ).strip()

            pincode = input(
                f"Pincode [{student['pincode'] or ''}]: "
            ).strip()

            emergency_contact = input(
                f"Emergency Contact "
                f"[{student['emergency_contact'] or ''}]: "
            ).strip()

            department_id = input(
                f"Department ID [{student['department_id']}]: "
            ).strip()

            first_name = first_name or student["first_name"]
            last_name = last_name or student["last_name"]
            phone = phone or student["phone"]
            city = city or student["city"]
            state = state or student["state"]
            pincode = pincode or student["pincode"]
            emergency_contact = (
                emergency_contact
                or student["emergency_contact"]
            )

            if department_id:
                if not department_id.isdigit():
                    print("\nInvalid department ID.")
                    return

                department_id = int(department_id)
            else:
                department_id = student["department_id"]

            update_user_query = """
                UPDATE users
                SET
                    first_name = %s,
                    last_name = %s,
                    phone = %s
                WHERE user_id = %s
            """

            cursor.execute(
                update_user_query,
                (
                    first_name,
                    last_name,
                    phone,
                    student["user_id"]
                )
            )

            update_student_query = """
                UPDATE student
                SET
                    department_id = %s,
                    city = %s,
                    state = %s,
                    pincode = %s,
                    emergency_contact = %s
                WHERE student_id = %s
            """

            cursor.execute(
                update_student_query,
                (
                    department_id,
                    city,
                    state,
                    pincode,
                    emergency_contact,
                    int(student_id)
                )
            )

            connection.commit()

            print("\nStudent updated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to update student.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def deactivate_student(self):

        print("\n================================")
        print("       DEACTIVATE STUDENT")
        print("================================")

        student_id = input("Enter Student ID: ").strip()

        if not student_id.isdigit():
            print("\nInvalid Student ID.")
            return

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    s.student_id,
                    s.user_id,
                    u.first_name,
                    u.middle_name,
                    u.last_name,
                    u.email,
                    u.status AS user_status,
                    s.student_status
                FROM student s
                INNER JOIN users u
                    ON s.user_id = u.user_id
                WHERE s.student_id = %s
            """

            cursor.execute(query, (int(student_id),))

            student = cursor.fetchone()

            if student is None:
                print("\nStudent not found.")
                return

            print("\nStudent Information")
            print("-------------------")
            print(
                "Name:",
                student["first_name"],
                student["middle_name"] or "",
                student["last_name"]
            )
            print("Email:", student["email"])
            print("Current User Status:", student["user_status"])
            print("Current Student Status:", student["student_status"])

            if student["student_status"] != "ACTIVE":
                print("\nStudent is already inactive.")
                return

            confirm = input(
                "\nAre you sure you want to deactivate this student? (YES/NO): "
            ).strip().upper()

            if confirm != "YES":
                print("\nDeactivation cancelled.")
                return

            update_user_query = """
                UPDATE users
                SET status = 'INACTIVE'
                WHERE user_id = %s
            """

            cursor.execute(
                update_user_query,
                (student["user_id"],)
            )

            update_student_query = """
                UPDATE student
                SET student_status = 'SUSPENDED'
                WHERE student_id = %s
            """

            cursor.execute(
                update_student_query,
                (int(student_id),)
            )

            connection.commit()

            print("\nStudent deactivated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to deactivate student.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def manage_faculty(self, user):

        while True:

            print("\n================================")
            print("         MANAGE FACULTY")
            print("================================")

            print("1. View All Faculty")
            print("2. View Faculty Details")
            print("3. Add Faculty")
            print("4. Update Faculty")
            print("5. Deactivate Faculty")
            print("6. Back")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                 self.view_all_faculty()

            elif choice == "2":
                self.view_faculty_details()

            elif choice == "3":
                self.add_faculty()

            elif choice == "4":
                self.update_faculty()

            elif choice == "5":
                 self.deactivate_faculty()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")


    def view_all_faculty(self):

        print("\n================================")
        print("          ALL FACULTY")
        print("================================")

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    f.faculty_id,
                    u.user_id,
                    u.first_name,
                    u.middle_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    d.department_name,
                    d.department_code,
                    f.designation,
                    f.qualification,
                    f.joining_date,
                    f.employment_type,
                    f.status
                FROM faculty f
                INNER JOIN users u
                    ON f.user_id = u.user_id
                INNER JOIN department d
                    ON f.department_id = d.department_id
                ORDER BY f.faculty_id
            """

            cursor.execute(query)

            faculty_list = cursor.fetchall()

            if not faculty_list:
                print("\nNo faculty records found.")
                return

            for faculty in faculty_list:

                full_name = " ".join(
                    part
                    for part in [
                        faculty["first_name"],
                        faculty["middle_name"],
                        faculty["last_name"]
                    ]
                    if part
                )

                print("\n--------------------------------")
                print("Faculty ID:", faculty["faculty_id"])
                print("User ID:", faculty["user_id"])
                print("Name:", full_name)
                print("Email:", faculty["email"])
                print("Phone:", faculty["phone"])
                print("Department:", faculty["department_name"])
                print("Department Code:", faculty["department_code"])
                print("Designation:", faculty["designation"])
                print("Qualification:", faculty["qualification"])
                print("Joining Date:", faculty["joining_date"])
                print("Employment Type:", faculty["employment_type"])
                print("Status:", faculty["status"])

        except Exception as error:

            print("\nFailed to load faculty.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def view_faculty_details(self):

        print("\n================================")
        print("        FACULTY DETAILS")
        print("================================")

        faculty_id = input("Enter Faculty ID: ").strip()

        if not faculty_id.isdigit():
            print("\nInvalid Faculty ID.")
            return

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    f.faculty_id,
                    u.user_id,
                    u.first_name,
                    u.middle_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    u.role,
                    u.status AS user_status,

                    d.department_name,
                    d.department_code,

                    f.date_of_birth,
                    f.gender,
                    f.blood_group,
                    f.father_name,
                    f.mother_name,
                    f.address,
                    f.city,
                    f.state,
                    f.pincode,
                    f.designation,
                    f.qualification,
                    f.specialization,
                    f.joining_date,
                    f.salary,
                    f.employment_type,
                    f.emergency_contact,
                    f.status AS faculty_status

                FROM faculty f

                INNER JOIN users u
                    ON f.user_id = u.user_id

                INNER JOIN department d
                    ON f.department_id = d.department_id

                WHERE f.faculty_id = %s
            """

            cursor.execute(query, (int(faculty_id),))

            faculty = cursor.fetchone()

            if faculty is None:
                print("\nFaculty not found.")
                return

            full_name = " ".join(
                part
                for part in [
                    faculty["first_name"],
                    faculty["middle_name"],
                    faculty["last_name"]
                ]
                if part
            )

            print("\n================================")
            print("       ACCOUNT INFORMATION")
            print("================================")

            print("User ID:", faculty["user_id"])
            print("Faculty ID:", faculty["faculty_id"])
            print("Name:", full_name)
            print("Email:", faculty["email"])
            print("Phone:", faculty["phone"])
            print("Role:", faculty["role"])
            print("Account Status:", faculty["user_status"])

            print("\n================================")
            print("      PROFESSIONAL INFORMATION")
            print("================================")

            print("Department:", faculty["department_name"])
            print("Department Code:", faculty["department_code"])
            print("Designation:", faculty["designation"])
            print("Qualification:", faculty["qualification"])
            print("Specialization:", faculty["specialization"])
            print("Joining Date:", faculty["joining_date"])
            print("Salary:", faculty["salary"])
            print("Employment Type:", faculty["employment_type"])
            print("Faculty Status:", faculty["faculty_status"])

            print("\n================================")
            print("        PERSONAL INFORMATION")
            print("================================")

            print("Date of Birth:", faculty["date_of_birth"])
            print("Gender:", faculty["gender"])
            print("Blood Group:", faculty["blood_group"])
            print("Father Name:", faculty["father_name"])
            print("Mother Name:", faculty["mother_name"])

            print("\n================================")
            print("         ADDRESS INFORMATION")
            print("================================")

            print("Address:", faculty["address"])
            print("City:", faculty["city"])
            print("State:", faculty["state"])
            print("Pincode:", faculty["pincode"])
            print("Emergency Contact:", faculty["emergency_contact"])

        except Exception as error:

            print("\nFailed to load faculty details.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def add_faculty(self):

        print("\n================================")
        print("           ADD FACULTY")
        print("================================")

        print("\n--- Account Information ---")

        first_name = input("First Name: ").strip()
        middle_name = input("Middle Name (optional): ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        phone = input("Phone: ").strip()
        password = input("Password: ")

        print("\n--- Professional Information ---")

        department_id = input("Department ID: ").strip()
        designation = input("Designation: ").strip()
        qualification = input("Qualification: ").strip()
        specialization = input(
            "Specialization (optional): "
        ).strip()

        joining_date = input(
            "Joining Date (YYYY-MM-DD): "
        ).strip()

        salary = input("Salary: ").strip()

        employment_type = input(
            "Employment Type (FULL_TIME/PART_TIME/CONTRACT): "
        ).strip().upper()

        print("\n--- Personal Information ---")

        date_of_birth = input(
            "Date of Birth (YYYY-MM-DD): "
        ).strip()

        gender = input(
            "Gender (MALE/FEMALE/OTHER): "
        ).strip().upper()

        blood_group = input(
            "Blood Group (A+/A-/B+/B-/AB+/AB-/O+/O-): "
        ).strip().upper()

        father_name = input(
            "Father Name (optional): "
        ).strip()

        mother_name = input(
            "Mother Name (optional): "
        ).strip()

        print("\n--- Address Information ---")

        address = input("Address: ").strip()
        city = input("City: ").strip()
        state = input("State: ").strip()
        pincode = input("Pincode: ").strip()

        emergency_contact = input(
            "Emergency Contact: "
        ).strip()

        if not first_name or not last_name:
            print("\nFirst name and last name are required.")
            return

        if not email or not phone or not password:
            print("\nEmail, phone and password are required.")
            return

        if not department_id.isdigit():
            print("\nInvalid department ID.")
            return

        if gender not in ("MALE", "FEMALE", "OTHER"):
            print("\nInvalid gender.")
            return

        valid_blood_groups = (
            "A+", "A-",
            "B+", "B-",
            "AB+", "AB-",
            "O+", "O-"
        )

        if blood_group and blood_group not in valid_blood_groups:
            print("\nInvalid blood group.")
            return

        valid_employment_types = (
            "FULL_TIME",
            "PART_TIME",
            "CONTRACT"
        )

        if employment_type not in valid_employment_types:
            print("\nInvalid employment type.")
            return

        try:
            salary = float(salary)
        except ValueError:
            print("\nInvalid salary.")
            return

        connection = create_connection()
        cursor = connection.cursor()

        try:

            check_query = """
                SELECT user_id
                FROM users
                WHERE email = %s
            """

            cursor.execute(
                check_query,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user is not None:
                print("\nEmail already exists.")
                connection.rollback()
                return

            password_hash = hash_password(password)

            user_query = """
                INSERT INTO users (
                    first_name,
                    middle_name,
                    last_name,
                    email,
                    phone,
                    password_hash,
                    role,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    'FACULTY', 'ACTIVE'
                )
            """

            cursor.execute(
                user_query,
                (
                    first_name,
                    middle_name if middle_name else None,
                    last_name,
                    email,
                    phone,
                    password_hash
                )
            )

            user_id = cursor.lastrowid

            faculty_query = """
                INSERT INTO faculty (
                    user_id,
                    department_id,
                    date_of_birth,
                    gender,
                    blood_group,
                    father_name,
                    mother_name,
                    address,
                    city,
                    state,
                    pincode,
                    designation,
                    qualification,
                    specialization,
                    joining_date,
                    salary,
                    employment_type,
                    emergency_contact,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, 'ACTIVE'
                )
            """

            cursor.execute(
                faculty_query,
                (
                    user_id,
                    int(department_id),
                    date_of_birth,
                    gender,
                    blood_group if blood_group else None,
                    father_name if father_name else None,
                    mother_name if mother_name else None,
                    address,
                    city,
                    state,
                    pincode,
                    designation,
                    qualification,
                    specialization if specialization else None,
                    joining_date,
                    salary,
                    employment_type,
                    emergency_contact
                )
            )

            faculty_id = cursor.lastrowid

            connection.commit()

            print("\nFaculty added successfully.")
            print("User ID:", user_id)
            print("Faculty ID:", faculty_id)

        except Exception as error:

            connection.rollback()

            print("\nFailed to add faculty.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def update_faculty(self):

        print("\n================================")
        print("         UPDATE FACULTY")
        print("================================")

        faculty_id = input("Enter Faculty ID: ").strip()

        if not faculty_id.isdigit():
            print("\nInvalid Faculty ID.")
            return

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    f.faculty_id,
                    f.user_id,
                    u.first_name,
                    u.middle_name,
                    u.last_name,
                    u.email,
                    u.phone,
                    f.department_id,
                    f.designation,
                    f.qualification,
                    f.specialization,
                    f.salary,
                    f.employment_type,
                    f.city,
                    f.state,
                    f.pincode,
                    f.emergency_contact,
                    f.status
                FROM faculty f
                INNER JOIN users u
                    ON f.user_id = u.user_id
                WHERE f.faculty_id = %s
            """

            cursor.execute(query, (int(faculty_id),))

            faculty = cursor.fetchone()

            if faculty is None:
                print("\nFaculty not found.")
                return

            print("\nCurrent Faculty Information")
            print("---------------------------")

            full_name = " ".join(
                part
                for part in [
                    faculty["first_name"],
                    faculty["middle_name"],
                    faculty["last_name"]
                ]
                if part
            )

            print("Name:", full_name)
            print("Email:", faculty["email"])
            print("Phone:", faculty["phone"])
            print("Department ID:", faculty["department_id"])
            print("Designation:", faculty["designation"])
            print("Qualification:", faculty["qualification"])
            print("Specialization:", faculty["specialization"])
            print("Salary:", faculty["salary"])
            print("Employment Type:", faculty["employment_type"])
            print("City:", faculty["city"])

            print("\nEnter new values.")
            print("Press ENTER to keep the current value.")

            first_name = input(
                f"First Name [{faculty['first_name']}]: "
            ).strip()

            last_name = input(
                f"Last Name [{faculty['last_name']}]: "
            ).strip()

            phone = input(
                f"Phone [{faculty['phone']}]: "
            ).strip()

            department_id = input(
                f"Department ID [{faculty['department_id']}]: "
            ).strip()

            designation = input(
                f"Designation [{faculty['designation']}]: "
            ).strip()

            qualification = input(
                f"Qualification [{faculty['qualification']}]: "
            ).strip()

            specialization = input(
                f"Specialization [{faculty['specialization'] or ''}]: "
            ).strip()

            salary = input(
                f"Salary [{faculty['salary']}]: "
            ).strip()

            employment_type = input(
                f"Employment Type [{faculty['employment_type']}]: "
            ).strip().upper()

            city = input(
                f"City [{faculty['city'] or ''}]: "
            ).strip()

            state = input(
                f"State [{faculty['state'] or ''}]: "
            ).strip()

            pincode = input(
                f"Pincode [{faculty['pincode'] or ''}]: "
            ).strip()

            emergency_contact = input(
                f"Emergency Contact "
                f"[{faculty['emergency_contact'] or ''}]: "
            ).strip()

            first_name = first_name or faculty["first_name"]
            last_name = last_name or faculty["last_name"]
            phone = phone or faculty["phone"]
            designation = designation or faculty["designation"]
            qualification = qualification or faculty["qualification"]
            specialization = (
                specialization
                or faculty["specialization"]
            )
            city = city or faculty["city"]
            state = state or faculty["state"]
            pincode = pincode or faculty["pincode"]
            emergency_contact = (
                emergency_contact
                or faculty["emergency_contact"]
            )

            if department_id:
                if not department_id.isdigit():
                    print("\nInvalid department ID.")
                    return

                department_id = int(department_id)
            else:
                department_id = faculty["department_id"]

            if salary:
                try:
                    salary = float(salary)
                except ValueError:
                    print("\nInvalid salary.")
                    return
            else:
                salary = faculty["salary"]

            valid_employment_types = (
                "FULL_TIME",
                "PART_TIME",
                "CONTRACT"
            )

            if employment_type:
                if employment_type not in valid_employment_types:
                    print("\nInvalid employment type.")
                    return
            else:
                employment_type = faculty["employment_type"]

            update_user_query = """
                UPDATE users
                SET
                    first_name = %s,
                    last_name = %s,
                    phone = %s
                WHERE user_id = %s
            """

            cursor.execute(
                update_user_query,
                (
                    first_name,
                    last_name,
                    phone,
                    faculty["user_id"]
                )
            )

            update_faculty_query = """
                UPDATE faculty
                SET
                    department_id = %s,
                    designation = %s,
                    qualification = %s,
                    specialization = %s,
                    salary = %s,
                    employment_type = %s,
                    city = %s,
                    state = %s,
                    pincode = %s,
                    emergency_contact = %s
                WHERE faculty_id = %s
            """

            cursor.execute(
                update_faculty_query,
                (
                    department_id,
                    designation,
                    qualification,
                    specialization,
                    salary,
                    employment_type,
                    city,
                    state,
                    pincode,
                    emergency_contact,
                    int(faculty_id)
                )
            )

            connection.commit()

            print("\nFaculty updated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to update faculty.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def deactivate_faculty(self):

        print("\n================================")
        print("       DEACTIVATE FACULTY")
        print("================================")

        faculty_id = input("Enter Faculty ID: ").strip()

        if not faculty_id.isdigit():
            print("\nInvalid Faculty ID.")
            return

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    f.faculty_id,
                    f.user_id,
                    u.first_name,
                    u.middle_name,
                    u.last_name,
                    u.email,
                    u.status AS user_status,
                    f.status AS faculty_status
                FROM faculty f
                INNER JOIN users u
                    ON f.user_id = u.user_id
                WHERE f.faculty_id = %s
            """

            cursor.execute(query, (int(faculty_id),))

            faculty = cursor.fetchone()

            if faculty is None:
                print("\nFaculty not found.")
                return

            full_name = " ".join(
                part
                for part in [
                    faculty["first_name"],
                    faculty["middle_name"],
                    faculty["last_name"]
                ]
                if part
            )

            print("\nFaculty Information")
            print("-------------------")
            print("Name:", full_name)
            print("Email:", faculty["email"])
            print("Current User Status:", faculty["user_status"])
            print("Current Faculty Status:", faculty["faculty_status"])

            if faculty["faculty_status"] != "ACTIVE":
                print("\nFaculty is already inactive.")
                return

            confirm = input(
                "\nAre you sure you want to deactivate this faculty? (YES/NO): "
            ).strip().upper()

            if confirm != "YES":
                print("\nDeactivation cancelled.")
                return

            update_user_query = """
                UPDATE users
                SET status = 'INACTIVE'
                WHERE user_id = %s
            """

            cursor.execute(
                update_user_query,
                (faculty["user_id"],)
            )

            update_faculty_query = """
                UPDATE faculty
                SET status = 'INACTIVE'
                WHERE faculty_id = %s
            """

            cursor.execute(
                update_faculty_query,
                (int(faculty_id),)
            )

            connection.commit()

            print("\nFaculty deactivated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to deactivate faculty.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def manage_courses(self, user):

        while True:

            print("\n================================")
            print("         MANAGE COURSES")
            print("================================")

            print("1. View All Courses")
            print("2. View Course Details")
            print("3. Add Course")
            print("4. Update Course")
            print("5. Delete Course")
            print("6. Back")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_all_courses()

            elif choice == "2":
                self.view_course_details()

            elif choice == "3":
                 self.add_course()

            elif choice == "4":
                self.update_course()

            elif choice == "5":
                self.delete_course()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")


    def view_all_courses(self):

        print("\n================================")
        print("          ALL COURSES")
        print("================================")

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    c.course_id,
                    c.course_name,
                    c.course_code,
                    c.degree_level,
                    d.department_name,
                    d.department_code
                FROM course c
                LEFT JOIN department d
                    ON c.department_id = d.department_id
                ORDER BY c.course_id
            """

            cursor.execute(query)

            courses = cursor.fetchall()

            if not courses:
                print("\nNo courses found.")
                return

            for course in courses:

                print("\n--------------------------------")
                print("Course ID:", course["course_id"])
                print("Course Name:", course["course_name"])
                print("Course Code:", course["course_code"])
                print("Degree Level:", course["degree_level"])
                print("Department:", course["department_name"])
                print("Department Code:", course["department_code"])

        except Exception as error:

            print("\nFailed to load courses.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def view_course_details(self):

        print("\n================================")
        print("        COURSE DETAILS")
        print("================================")

        course_id = input("Enter Course ID: ")

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    c.course_id,
                    c.course_name,
                    c.course_code,
                    c.degree_level,
                    d.department_name,
                    d.department_code
                FROM course c
                LEFT JOIN department d
                    ON c.department_id = d.department_id
                WHERE c.course_id = %s
            """

            cursor.execute(query, (course_id,))

            course = cursor.fetchone()

            if not course:
                print("\nCourse not found.")
                return

            print("\n--------------------------------")
            print("Course ID:", course["course_id"])
            print("Course Name:", course["course_name"])
            print("Course Code:", course["course_code"])
            print("Degree Level:", course["degree_level"])
            print("Department:", course["department_name"])
            print("Department Code:", course["department_code"])

        except Exception as error:

            print("\nFailed to load course details.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def add_course(self):

        print("\n================================")
        print("           ADD COURSE")
        print("================================")

        course_name = input("Course Name: ").strip()
        course_code = input("Course Code: ").strip()
        duration_years = input("Duration (Years): ").strip()
        degree_level = input("Degree Level (DIPLOMA/UG/PG/PHD): ").strip().upper()
        department_id = input("Department ID: ").strip()

        if not course_name or not course_code or not duration_years or not degree_level or not department_id:
            print("\nAll fields are required.")
            return

        try:
            duration_years = int(duration_years)
            department_id = int(department_id)
        except ValueError:
            print("\nDuration and Department ID must be numbers.")
            return

        connection = create_connection()
        cursor = connection.cursor()

        try:

            query = """
                INSERT INTO course (
                    course_name,
                    course_code,
                    duration_years,
                    degree_level,
                    department_id
                )
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    course_name,
                    course_code,
                    duration_years,
                    degree_level,
                    department_id
                )
            )

            connection.commit()

            print("\nCourse added successfully!")
            print("Course ID:", cursor.lastrowid)

        except Exception as error:

            connection.rollback()

            print("\nFailed to add course.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def update_course(self):

        print("\n================================")
        print("          UPDATE COURSE")
        print("================================")

        course_id = input("Enter Course ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    course_id,
                    course_name,
                    course_code,
                    duration_years,
                    degree_level,
                    department_id
                FROM course
                WHERE course_id = %s
                """,
                (course_id,)
            )

            course = cursor.fetchone()

            if not course:
                print("\nCourse not found.")
                return

            print("\nCurrent Course Details:")
            print("Course Name:", course["course_name"])
            print("Course Code:", course["course_code"])
            print("Duration:", course["duration_years"])
            print("Degree Level:", course["degree_level"])
            print("Department ID:", course["department_id"])

            print("\nEnter New Details")

            course_name = input("Course Name: ").strip()
            course_code = input("Course Code: ").strip()
            duration_years = input("Duration (Years): ").strip()
            degree_level = input(
                "Degree Level (DIPLOMA/UG/PG/PHD): "
            ).strip().upper()
            department_id = input("Department ID: ").strip()

            if not course_name or not course_code or not duration_years \
                    or not degree_level or not department_id:
                print("\nAll fields are required.")
                return

            try:
                duration_years = int(duration_years)
                department_id = int(department_id)
            except ValueError:
                print("\nDuration and Department ID must be numbers.")
                return

            cursor.execute(
                """
                UPDATE course
                SET
                    course_name = %s,
                    course_code = %s,
                    duration_years = %s,
                    degree_level = %s,
                    department_id = %s
                WHERE course_id = %s
                """,
                (
                    course_name,
                    course_code,
                    duration_years,
                    degree_level,
                    department_id,
                    course_id
                )
            )

            connection.commit()

            print("\nCourse updated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to update course.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def delete_course(self):

        print("\n================================")
        print("          DELETE COURSE")
        print("================================")

        course_id = input("Enter Course ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    course_id,
                    course_name,
                    course_code
                FROM course
                WHERE course_id = %s
                """,
                (course_id,)
            )

            course = cursor.fetchone()

            if not course:
                print("\nCourse not found.")
                return

            print("\nCourse Found:")
            print("Course ID:", course["course_id"])
            print("Course Name:", course["course_name"])
            print("Course Code:", course["course_code"])

            confirmation = input(
                "\nAre you sure you want to delete this course? (YES/NO): "
            ).strip().upper()

            if confirmation != "YES":
                print("\nDeletion cancelled.")
                return

            cursor.execute(
                """
                DELETE FROM course
                WHERE course_id = %s
                """,
                (course_id,)
            )

            connection.commit()

            print("\nCourse deleted successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to delete course.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()



    def manage_subjects(self, user):

        while True:

            print("\n================================")
            print("         MANAGE SUBJECTS")
            print("================================")
            print("1. View All Subjects")
            print("2. View Subject Details")
            print("3. Add Subject")
            print("4. Update Subject")
            print("5. Delete Subject")
            print("6. Back")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_all_subjects()

            elif choice == "2":
                self.view_subject_details()

            elif choice == "3":
                self.add_subject()

            elif choice == "4":
                self.update_subject()

            elif choice == "5":
                self.delete_subject()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")


    def view_all_subjects(self):

        print("\n================================")
        print("          ALL SUBJECTS")
        print("================================")

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    s.subject_id,
                    s.subject_code,
                    s.subject_name,
                    s.credits,
                    s.semester,
                    s.subject_type,
                    d.department_name,
                    d.department_code
                FROM subject s
                LEFT JOIN department d
                    ON s.department_id = d.department_id
                ORDER BY s.subject_id
            """

            cursor.execute(query)

            subjects = cursor.fetchall()

            if not subjects:
                print("\nNo subjects found.")
                return

            for subject in subjects:

                print("\n--------------------------------")
                print("Subject ID:", subject["subject_id"])
                print("Subject Code:", subject["subject_code"])
                print("Subject Name:", subject["subject_name"])
                print("Credits:", subject["credits"])
                print("Semester:", subject["semester"])
                print("Subject Type:", subject["subject_type"])
                print("Department:", subject["department_name"])
                print("Department Code:", subject["department_code"])

        except Exception as error:

            print("\nFailed to load subjects.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def view_subject_details(self):

        print("\n================================")
        print("        SUBJECT DETAILS")
        print("================================")

        subject_id = input("Enter Subject ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    s.subject_id,
                    s.subject_code,
                    s.subject_name,
                    s.credits,
                    s.semester,
                    s.subject_type,
                    d.department_name,
                    d.department_code
                FROM subject s
                LEFT JOIN department d
                    ON s.department_id = d.department_id
                WHERE s.subject_id = %s
            """

            cursor.execute(query, (subject_id,))

            subject = cursor.fetchone()

            if not subject:
                print("\nSubject not found.")
                return

            print("\n--------------------------------")
            print("Subject ID:", subject["subject_id"])
            print("Subject Code:", subject["subject_code"])
            print("Subject Name:", subject["subject_name"])
            print("Credits:", subject["credits"])
            print("Semester:", subject["semester"])
            print("Subject Type:", subject["subject_type"])
            print("Department:", subject["department_name"])
            print("Department Code:", subject["department_code"])

        except Exception as error:

            print("\nFailed to load subject details.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def add_subject(self):

        print("\n================================")
        print("           ADD SUBJECT")
        print("================================")

        subject_code = input("Subject Code: ").strip()
        subject_name = input("Subject Name: ").strip()
        credits = input("Credits: ").strip()
        semester = input("Semester: ").strip()
        subject_type = input(
            "Subject Type (THEORY/LAB/TUTORIAL): "
        ).strip().upper()
        department_id = input("Department ID: ").strip()

        if not subject_code or not subject_name or not credits \
                or not semester or not subject_type or not department_id:
            print("\nAll fields are required.")
            return

        try:
            credits = int(credits)
            semester = int(semester)
            department_id = int(department_id)
        except ValueError:
            print("\nCredits, Semester and Department ID must be numbers.")
            return

        if subject_type not in ["THEORY", "LAB", "TUTORIAL"]:
            print("\nInvalid subject type.")
            return

        connection = create_connection()
        cursor = connection.cursor()

        try:

            query = """
                INSERT INTO subject (
                    subject_code,
                    subject_name,
                    credits,
                    semester,
                    subject_type,
                    department_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    subject_code,
                    subject_name,
                    credits,
                    semester,
                    subject_type,
                    department_id
                )
            )

            connection.commit()

            print("\nSubject added successfully!")
            print("Subject ID:", cursor.lastrowid)

        except Exception as error:

            connection.rollback()

            print("\nFailed to add subject.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def update_subject(self):

        print("\n================================")
        print("          UPDATE SUBJECT")
        print("================================")

        subject_id = input("Enter Subject ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    subject_id,
                    subject_code,
                    subject_name,
                    credits,
                    semester,
                    subject_type,
                    department_id
                FROM subject
                WHERE subject_id = %s
                """,
                (subject_id,)
            )

            subject = cursor.fetchone()

            if not subject:
                print("\nSubject not found.")
                return

            print("\nCurrent Subject Details:")
            print("Subject Code:", subject["subject_code"])
            print("Subject Name:", subject["subject_name"])
            print("Credits:", subject["credits"])
            print("Semester:", subject["semester"])
            print("Subject Type:", subject["subject_type"])
            print("Department ID:", subject["department_id"])

            print("\nEnter New Details")

            subject_code = input("Subject Code: ").strip()
            subject_name = input("Subject Name: ").strip()
            credits = input("Credits: ").strip()
            semester = input("Semester: ").strip()
            subject_type = input(
                "Subject Type (THEORY/LAB/TUTORIAL): "
            ).strip().upper()
            department_id = input("Department ID: ").strip()

            if not subject_code or not subject_name or not credits \
                    or not semester or not subject_type or not department_id:
                print("\nAll fields are required.")
                return

            try:
                credits = int(credits)
                semester = int(semester)
                department_id = int(department_id)
            except ValueError:
                print("\nCredits, Semester and Department ID must be numbers.")
                return

            if subject_type not in ["THEORY", "LAB", "TUTORIAL"]:
                print("\nInvalid subject type.")
                return

            cursor.execute(
                """
                UPDATE subject
                SET
                    subject_code = %s,
                    subject_name = %s,
                    credits = %s,
                    semester = %s,
                    subject_type = %s,
                    department_id = %s
                WHERE subject_id = %s
                """,
                (
                    subject_code,
                    subject_name,
                    credits,
                    semester,
                    subject_type,
                    department_id,
                    subject_id
                )
            )

            connection.commit()

            print("\nSubject updated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to update subject.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def delete_subject(self):

        print("\n================================")
        print("          DELETE SUBJECT")
        print("================================")

        subject_id = input("Enter Subject ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    subject_id,
                    subject_code,
                    subject_name
                FROM subject
                WHERE subject_id = %s
                """,
                (subject_id,)
            )

            subject = cursor.fetchone()

            if not subject:
                print("\nSubject not found.")
                return

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM class_session
                WHERE subject_id = %s
                """,
                (subject_id,)
            )

            result = cursor.fetchone()

            if result["total"] > 0:

                print("\nCannot delete this subject.")
                print(
                    "This subject is already used by",
                    result["total"],
                    "class session(s)."
                )
                print(
                    "Delete or reassign those class sessions first."
                )
                return

            print("\nSubject Found:")
            print("Subject ID:", subject["subject_id"])
            print("Subject Code:", subject["subject_code"])
            print("Subject Name:", subject["subject_name"])

            confirmation = input(
                "\nAre you sure you want to delete this subject? (YES/NO): "
            ).strip().upper()

            if confirmation != "YES":
                print("\nDeletion cancelled.")
                return

            cursor.execute(
                """
                DELETE FROM subject
                WHERE subject_id = %s
                """,
                (subject_id,)
            )

            connection.commit()

            print("\nSubject deleted successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to delete subject.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def manage_notices(self, user):

        while True:

            print("\n================================")
            print("          MANAGE NOTICES")
            print("================================")
            print("1. View All Notices")
            print("2. View Notice Details")
            print("3. Add Notice")
            print("4. Update Notice")
            print("5. Delete Notice")
            print("6. Back")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_all_notices()

            elif choice == "2":
                self.view_notice_details()

            elif choice == "3":
                self.add_notice(user)

            elif choice == "4":
                self.update_notice()

            elif choice == "5":
                self.delete_notice()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")


    def view_all_notices(self):

        print("\n================================")
        print("           ALL NOTICES")
        print("================================")

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    notice_id,
                    title,
                    release_date,
                    valid_till,
                    target_role,
                    is_active,
                    created_by
                FROM notice
                ORDER BY notice_id DESC
            """

            cursor.execute(query)

            notices = cursor.fetchall()

            if not notices:
                print("\nNo notices found.")
                return

            for notice in notices:

                print("\n--------------------------------")
                print("Notice ID:", notice["notice_id"])
                print("Title:", notice["title"])
                print("Release Date:", notice["release_date"])
                print("Valid Till:", notice["valid_till"])
                print("Target Role:", notice["target_role"])
                print("Active:", notice["is_active"])
                print("Created By:", notice["created_by"])

        except Exception as error:

            print("\nFailed to load notices.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def view_notice_details(self):

        print("\n================================")
        print("         NOTICE DETAILS")
        print("================================")

        notice_id = input("Enter Notice ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    notice_id,
                    title,
                    content,
                    release_date,
                    valid_till,
                    target_role,
                    created_by,
                    is_active,
                    created_at,
                    updated_at
                FROM notice
                WHERE notice_id = %s
            """

            cursor.execute(query, (notice_id,))

            notice = cursor.fetchone()

            if not notice:
                print("\nNotice not found.")
                return

            print("\n--------------------------------")
            print("Notice ID:", notice["notice_id"])
            print("Title:", notice["title"])
            print("Content:", notice["content"])
            print("Release Date:", notice["release_date"])
            print("Valid Till:", notice["valid_till"])
            print("Target Role:", notice["target_role"])
            print("Created By:", notice["created_by"])
            print("Active:", notice["is_active"])
            print("Created At:", notice["created_at"])
            print("Updated At:", notice["updated_at"])

        except Exception as error:

            print("\nFailed to load notice details.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def add_notice(self, user):

        print("\n================================")
        print("            ADD NOTICE")
        print("================================")

        title = input("Title: ").strip()
        content = input("Content: ").strip()
        release_date = input("Release Date (YYYY-MM-DD): ").strip()
        valid_till = input("Valid Till (YYYY-MM-DD): ").strip()
        target_role = input(
            "Target Role (STUDENT/FACULTY/ADMIN/ALL): "
        ).strip().upper()

        if not title or not content or not release_date or not target_role:
            print("\nRequired fields cannot be empty.")
            return

        if target_role not in ["STUDENT", "FACULTY", "ADMIN", "ALL"]:
            print("\nInvalid target role.")
            return

        connection = create_connection()
        cursor = connection.cursor()

        try:

            query = """
                INSERT INTO notice (
                    title,
                    content,
                    release_date,
                    valid_till,
                    target_role,
                    created_by,
                    is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, 1)
            """

            cursor.execute(
                query,
                (
                    title,
                    content,
                    release_date,
                    valid_till if valid_till else None,
                    target_role,
                    user.user_id
                )
            )

            connection.commit()

            print("\nNotice added successfully!")
            print("Notice ID:", cursor.lastrowid)

        except Exception as error:

            connection.rollback()

            print("\nFailed to add notice.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()

    def update_notice(self):

        print("\n================================")
        print("          UPDATE NOTICE")
        print("================================")

        notice_id = input("Enter Notice ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    notice_id,
                    title,
                    content,
                    release_date,
                    valid_till,
                    target_role,
                    is_active
                FROM notice
                WHERE notice_id = %s
                """,
                (notice_id,)
            )

            notice = cursor.fetchone()

            if not notice:
                print("\nNotice not found.")
                return

            print("\nCurrent Notice Details:")
            print("Title:", notice["title"])
            print("Content:", notice["content"])
            print("Release Date:", notice["release_date"])
            print("Valid Till:", notice["valid_till"])
            print("Target Role:", notice["target_role"])
            print("Active:", notice["is_active"])

            print("\nEnter New Details")

            title = input("Title: ").strip()
            content = input("Content: ").strip()
            release_date = input(
                "Release Date (YYYY-MM-DD): "
            ).strip()
            valid_till = input(
                "Valid Till (YYYY-MM-DD): "
            ).strip()
            target_role = input(
                "Target Role (STUDENT/FACULTY/ADMIN/ALL): "
            ).strip().upper()

            if not title or not content or not release_date or not target_role:
                print("\nRequired fields cannot be empty.")
                return

            if target_role not in ["STUDENT", "FACULTY", "ADMIN", "ALL"]:
                print("\nInvalid target role.")
                return

            cursor.execute(
                """
                UPDATE notice
                SET
                    title = %s,
                    content = %s,
                    release_date = %s,
                    valid_till = %s,
                    target_role = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE notice_id = %s
                """,
                (
                    title,
                    content,
                    release_date,
                    valid_till if valid_till else None,
                    target_role,
                    notice_id
                )
            )

            connection.commit()

            print("\nNotice updated successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to update notice.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()


    def delete_notice(self):

        print("\n================================")
        print("          DELETE NOTICE")
        print("================================")

        notice_id = input("Enter Notice ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    notice_id,
                    title,
                    target_role
                FROM notice
                WHERE notice_id = %s
                """,
                (notice_id,)
            )

            notice = cursor.fetchone()

            if not notice:
                print("\nNotice not found.")
                return

            print("\nNotice Found:")
            print("Notice ID:", notice["notice_id"])
            print("Title:", notice["title"])
            print("Target Role:", notice["target_role"])

            confirmation = input(
                "\nAre you sure you want to delete this notice? (YES/NO): "
            ).strip().upper()

            if confirmation != "YES":
                print("\nDeletion cancelled.")
                return

            cursor.execute(
                """
                DELETE FROM notice
                WHERE notice_id = %s
                """,
                (notice_id,)
            )

            connection.commit()

            print("\nNotice deleted successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to delete notice.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()



    def manage_leave_requests(self, user):

        while True:

            print("\n================================")
            print("       MANAGE LEAVE REQUESTS")
            print("================================")
            print("1. View All Leave Requests")
            print("2. View Leave Request Details")
            print("3. Approve Leave Request")
            print("4. Reject Leave Request")
            print("5. Back")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.view_all_leave_requests()

            elif choice == "2":
                self.view_leave_request_details()

            elif choice == "3":
                self.approve_leave_request(user)

            elif choice == "4":
                self.reject_leave_request(user)

            elif choice == "5":
                break

            else:
                print("\nInvalid choice.")


    def view_all_leave_requests(self):

        print("\n================================")
        print("       ALL LEAVE REQUESTS")
        print("================================")

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    lr.request_id,
                    lr.user_id,
                    CONCAT(
                        u.first_name, ' ',
                        COALESCE(u.middle_name, ''), ' ',
                        u.last_name
                    ) AS applicant_name,
                    u.email,
                    lr.from_date,
                    lr.to_date,
                    lr.reason,
                    lr.leave_type,
                    lr.curr_status,
                    lr.reviewed_by,
                    lr.applied_at
                FROM leave_request lr
                JOIN users u
                    ON lr.user_id = u.user_id
                ORDER BY lr.request_id DESC
            """

            cursor.execute(query)

            requests = cursor.fetchall()

            if not requests:
                print("\nNo leave requests found.")
                return

            for request in requests:

                print("\n--------------------------------")
                print("Request ID:", request["request_id"])
                print("User ID:", request["user_id"])
                print("Applicant:", request["applicant_name"])
                print("Email:", request["email"])
                print("From Date:", request["from_date"])
                print("To Date:", request["to_date"])
                print("Leave Type:", request["leave_type"])
                print("Reason:", request["reason"])
                print("Status:", request["curr_status"])
                print("Reviewed By:", request["reviewed_by"])
                print("Applied At:", request["applied_at"])

        except Exception as error:

            print("\nFailed to load leave requests.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()



    def view_leave_request_details(self):

        print("\n================================")
        print("      LEAVE REQUEST DETAILS")
        print("================================")

        request_id = input("Enter Request ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    lr.request_id,
                    lr.user_id,
                    CONCAT(
                        u.first_name, ' ',
                        COALESCE(u.middle_name, ''), ' ',
                        u.last_name
                    ) AS applicant_name,
                    u.email,
                    u.phone,
                    u.role,
                    lr.from_date,
                    lr.to_date,
                    lr.reason,
                    lr.leave_type,
                    lr.curr_status,
                    lr.reviewed_by,
                    lr.reviewer_comment,
                    lr.applied_at,
                    lr.reviewed_at,
                    lr.updated_at
                FROM leave_request lr
                JOIN users u
                    ON lr.user_id = u.user_id
                WHERE lr.request_id = %s
            """

            cursor.execute(query, (request_id,))

            request = cursor.fetchone()

            if not request:
                print("\nLeave request not found.")
                return

            print("\n--------------------------------")
            print("Request ID:", request["request_id"])
            print("User ID:", request["user_id"])
            print("Applicant:", request["applicant_name"])
            print("Email:", request["email"])
            print("Phone:", request["phone"])
            print("Role:", request["role"])
            print("From Date:", request["from_date"])
            print("To Date:", request["to_date"])
            print("Leave Type:", request["leave_type"])
            print("Reason:", request["reason"])
            print("Status:", request["curr_status"])
            print("Reviewed By:", request["reviewed_by"])
            print("Reviewer Comment:", request["reviewer_comment"])
            print("Applied At:", request["applied_at"])
            print("Reviewed At:", request["reviewed_at"])
            print("Updated At:", request["updated_at"])

        except Exception as error:

            print("\nFailed to load leave request details.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()



    def approve_leave_request(self, user):

        print("\n================================")
        print("       APPROVE LEAVE REQUEST")
        print("================================")

        request_id = input("Enter Request ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    request_id,
                    user_id,
                    curr_status
                FROM leave_request
                WHERE request_id = %s
                """,
                (request_id,)
            )

            request = cursor.fetchone()

            if not request:
                print("\nLeave request not found.")
                return

            if request["curr_status"] == "APPROVED":
                print("\nThis leave request is already approved.")
                return

            if request["curr_status"] == "REJECTED":
                print("\nThis leave request has already been rejected.")
                return

            reviewer_comment = input(
                "Reviewer Comment: "
            ).strip()

            cursor.execute(
                """
                UPDATE leave_request
                SET
                    curr_status = 'APPROVED',
                    reviewed_by = %s,
                    reviewer_comment = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE request_id = %s
                """,
                (
                    user.user_id,
                    reviewer_comment if reviewer_comment else None,
                    request_id
                )
            )

            connection.commit()

            print("\nLeave request approved successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to approve leave request.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()



    def reject_leave_request(self, user):

        print("\n================================")
        print("        REJECT LEAVE REQUEST")
        print("================================")

        request_id = input("Enter Request ID: ").strip()

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    request_id,
                    user_id,
                    curr_status
                FROM leave_request
                WHERE request_id = %s
                """,
                (request_id,)
            )

            request = cursor.fetchone()

            if not request:
                print("\nLeave request not found.")
                return

            if request["curr_status"] == "APPROVED":
                print("\nThis leave request is already approved.")
                return

            if request["curr_status"] == "REJECTED":
                print("\nThis leave request has already been rejected.")
                return

            reviewer_comment = input(
                "Reviewer Comment: "
            ).strip()

            if not reviewer_comment:
                print("\nReviewer comment is required when rejecting a request.")
                return

            cursor.execute(
                """
                UPDATE leave_request
                SET
                    curr_status = 'REJECTED',
                    reviewed_by = %s,
                    reviewer_comment = %s,
                    reviewed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE request_id = %s
                """,
                (
                    user.user_id,
                    reviewer_comment,
                    request_id
                )
            )

            connection.commit()

            print("\nLeave request rejected successfully.")

        except Exception as error:

            connection.rollback()

            print("\nFailed to reject leave request.")
            print("Error:", error)

        finally:

            cursor.close()
            connection.close()




    def manage_placement(self, user):

        while True:

            print("\n================================")
            print("        MANAGE PLACEMENT")
            print("================================")

            print("1. Manage Companies")
            print("2. Manage Placement Drives")
            print("3. View Student Applications")
            print("4. Manage Placement News")
            print("5. Back")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.manage_companies(user)

            elif choice == "2":
                self.manage_placement_drives(user)

            elif choice == "3":
                self.manage_student_applications()

            elif choice == "4":
                self.manage_placement_news(user)

            elif choice == "5":
                break

            else:
                print("\nInvalid choice.")


    def manage_companies(self, user):

        while True:

            print("\n================================")
            print("        MANAGE COMPANIES")
            print("================================")

            print("1. View All Companies")
            print("2. View Company Details")
            print("3. Add Company")
            print("4. Update Company")
            print("5. Delete Company")
            print("6. Back")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_all_companies()

            elif choice == "2":
                self.view_company_details()

            elif choice == "3":
                self.add_company()

            elif choice == "4":
                self.update_company()

            elif choice == "5":
                 self.delete_company()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")



    def view_all_companies(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                company_id,
                company_name
            FROM company
            ORDER BY company_name
        """

        cursor.execute(query)

        companies = cursor.fetchall()

        if not companies:

            print("\nNo companies found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("        ALL COMPANIES")
        print("================================")

        for company in companies:

            print("\n--------------------------------")
            print("Company ID:", company["company_id"])
            print("Company Name:", company["company_name"])

        cursor.close()
        connection.close()

    def view_company_details(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       COMPANY DETAILS")
        print("================================")

        company_id = input("Enter Company ID: ")

        if not company_id.isdigit():
            print("\nInvalid Company ID.")

            cursor.close()
            connection.close()

            return

        company_id = int(company_id)

        query = """
            SELECT
                company_id,
                company_name,
                industry_type,
                company_description,
                location,
                website,
                contact_email,
                contact_phone
            FROM company
            WHERE company_id = %s
        """

        cursor.execute(query, (company_id,))

        company = cursor.fetchone()

        if company is None:

            print("\nCompany not found.")

            cursor.close()
            connection.close()

            return

        print("\n--------------------------------")
        print("Company ID:", company["company_id"])
        print("Company Name:", company["company_name"])
        print("Industry Type:", company["industry_type"])
        print("Description:", company["company_description"])
        print("Location:", company["location"])
        print("Website:", company["website"])
        print("Contact Email:", company["contact_email"])
        print("Contact Phone:", company["contact_phone"])

        cursor.close()
        connection.close()



    def add_company(self):

        connection = create_connection()
        cursor = connection.cursor()

        print("\n================================")
        print("          ADD COMPANY")
        print("================================")

        company_name = input("Company Name: ")
        industry_type = input("Industry Type: ")
        company_description = input("Company Description: ")
        location = input("Location: ")
        website = input("Website: ")
        contact_email = input("Contact Email: ")
        contact_phone = input("Contact Phone: ")

        if not company_name.strip():
            print("\nCompany name is required.")

            cursor.close()
            connection.close()

            return

        if not industry_type.strip():
            print("\nIndustry type is required.")

            cursor.close()
            connection.close()

            return

        if not location.strip():
            print("\nLocation is required.")

            cursor.close()
            connection.close()

            return

        query = """
            INSERT INTO company (
                company_name,
                industry_type,
                company_description,
                location,
                website,
                contact_email,
                contact_phone
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            company_name,
            industry_type,
            company_description if company_description.strip() else None,
            location,
            website if website.strip() else None,
            contact_email if contact_email.strip() else None,
            contact_phone if contact_phone.strip() else None
        )

        try:

            cursor.execute(query, values)

            connection.commit()

            print("\nCompany added successfully.")
            print("Company ID:", cursor.lastrowid)

        except Exception as e:

            connection.rollback()

            print("\nFailed to add company.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()


    def update_company(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("         UPDATE COMPANY")
        print("================================")

        company_id = input("Enter Company ID: ")

        if not company_id.isdigit():
            print("\nInvalid Company ID.")

            cursor.close()
            connection.close()

            return

        company_id = int(company_id)

        query = """
            SELECT
                company_id,
                company_name,
                industry_type,
                company_description,
                location,
                website,
                contact_email,
                contact_phone
            FROM company
            WHERE company_id = %s
        """

        cursor.execute(query, (company_id,))
        company = cursor.fetchone()

        if company is None:
            print("\nCompany not found.")

            cursor.close()
            connection.close()

            return

        print("\nCurrent Company Details")
        print("--------------------------------")
        print("Company Name:", company["company_name"])
        print("Industry Type:", company["industry_type"])
        print("Description:", company["company_description"])
        print("Location:", company["location"])
        print("Website:", company["website"])
        print("Contact Email:", company["contact_email"])
        print("Contact Phone:", company["contact_phone"])

        print("\nEnter new details.")
        print("Press Enter to keep the existing value.")

        company_name = input("Company Name: ")
        industry_type = input("Industry Type: ")
        company_description = input("Company Description: ")
        location = input("Location: ")
        website = input("Website: ")
        contact_email = input("Contact Email: ")
        contact_phone = input("Contact Phone: ")

        company_name = company_name if company_name.strip() else company["company_name"]
        industry_type = industry_type if industry_type.strip() else company["industry_type"]
        company_description = (
            company_description
            if company_description.strip()
            else company["company_description"]
        )
        location = location if location.strip() else company["location"]
        website = website if website.strip() else company["website"]
        contact_email = contact_email if contact_email.strip() else company["contact_email"]
        contact_phone = contact_phone if contact_phone.strip() else company["contact_phone"]

        update_query = """
            UPDATE company
            SET
                company_name = %s,
                industry_type = %s,
                company_description = %s,
                location = %s,
                website = %s,
                contact_email = %s,
                contact_phone = %s
            WHERE company_id = %s
        """

        values = (
            company_name,
            industry_type,
            company_description,
            location,
            website,
            contact_email,
            contact_phone,
            company_id
        )

        try:

            cursor.execute(update_query, values)

            connection.commit()

            print("\nCompany updated successfully.")

        except Exception as e:

            connection.rollback()

            print("\nFailed to update company.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()


    def delete_company(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("         DELETE COMPANY")
        print("================================")

        company_id = input("Enter Company ID: ")

        if not company_id.isdigit():
            print("\nInvalid Company ID.")

            cursor.close()
            connection.close()

            return

        company_id = int(company_id)

        query = """
            SELECT
                company_id,
                company_name
            FROM company
            WHERE company_id = %s
        """

        cursor.execute(query, (company_id,))
        company = cursor.fetchone()

        if company is None:
            print("\nCompany not found.")

            cursor.close()
            connection.close()

            return

        print("\nCompany Found")
        print("--------------------------------")
        print("Company ID:", company["company_id"])
        print("Company Name:", company["company_name"])

        confirmation = input("\nAre you sure you want to delete this company? (YES/NO): ")

        if confirmation.strip().upper() != "YES":
            print("\nDeletion cancelled.")

            cursor.close()
            connection.close()

            return

        try:

            cursor.execute(
                "DELETE FROM company WHERE company_id = %s",
                (company_id,)
            )

            connection.commit()

            print("\nCompany deleted successfully.")

        except Exception as e:

            connection.rollback()

            print("\nCannot delete this company.")
            print("It may already be used by a placement drive.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()



    def manage_placement_drives(self, user):

        while True:

            print("\n================================")
            print("     MANAGE PLACEMENT DRIVES")
            print("================================")

            print("1. View All Placement Drives")
            print("2. View Placement Drive Details")
            print("3. Add Placement Drive")
            print("4. Update Placement Drive")
            print("5. Delete Placement Drive")
            print("6. Back")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_all_placement_drives()

            elif choice == "2":
               self.view_placement_drive_details()

            elif choice == "3":
                self.add_placement_drive(user)

            elif choice == "4":
                self.update_placement_drive()

            elif choice == "5":
                self.delete_placement_drive()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")



    def view_all_placement_drives(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                d.drive_id,
                d.drive_title,
                c.company_name,
                d.drive_date,
                d.job_role,
                d.job_location,
                d.package_in_lpa,
                d.role_description,
                d.minimum_cgpa,
                d.minimum_10th_percentage,
                d.minimum_12th_percentage,
                d.maximum_backlogs,
                d.eligible_degree,
                d.eligible_branch,
                d.application_deadline,
                d.created_by,
                d.created_at,
                d.drive_status
            FROM drive d
            INNER JOIN company c
                ON d.company_id = c.company_id
            ORDER BY d.drive_date ASC
        """

        cursor.execute(query)

        drives = cursor.fetchall()

        if not drives:

            print("\nNo placement drives found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("      ALL PLACEMENT DRIVES")
        print("================================")

        for drive in drives:

            print("\n--------------------------------")
            print("Drive ID:", drive["drive_id"])
            print("Drive Title:", drive["drive_title"])
            print("Company:", drive["company_name"])
            print("Drive Date:", drive["drive_date"])
            print("Job Role:", drive["job_role"])
            print("Job Location:", drive["job_location"])
            print("Package (LPA):", drive["package_in_lpa"])
            print("Role Description:", drive["role_description"])
            print("Minimum CGPA:", drive["minimum_cgpa"])
            print("Minimum 10th %:", drive["minimum_10th_percentage"])
            print("Minimum 12th %:", drive["minimum_12th_percentage"])
            print("Maximum Backlogs:", drive["maximum_backlogs"])
            print("Eligible Degree:", drive["eligible_degree"])
            print("Eligible Branch:", drive["eligible_branch"])
            print("Application Deadline:", drive["application_deadline"])
            print("Created By:", drive["created_by"])
            print("Created At:", drive["created_at"])
            print("Drive Status:", drive["drive_status"])

        cursor.close()
        connection.close()




    def view_placement_drive_details(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("     PLACEMENT DRIVE DETAILS")
        print("================================")

        drive_id = input("Enter Drive ID: ")

        if not drive_id.isdigit():
            print("\nInvalid Drive ID.")

            cursor.close()
            connection.close()

            return

        drive_id = int(drive_id)

        query = """
            SELECT
                d.drive_id,
                d.company_id,
                c.company_name,
                d.drive_title,
                d.drive_date,
                d.job_role,
                d.job_location,
                d.package_in_lpa,
                d.role_description,
                d.minimum_cgpa,
                d.minimum_10th_percentage,
                d.minimum_12th_percentage,
                d.maximum_backlogs,
                d.eligible_degree,
                d.eligible_branch,
                d.application_deadline,
                d.created_by,
                d.created_at,
                d.drive_status
            FROM drive d
            INNER JOIN company c
                ON d.company_id = c.company_id
            WHERE d.drive_id = %s
        """

        cursor.execute(query, (drive_id,))

        drive = cursor.fetchone()

        if drive is None:
            print("\nPlacement drive not found.")

            cursor.close()
            connection.close()

            return

        print("\n--------------------------------")
        print("Drive ID:", drive["drive_id"])
        print("Company ID:", drive["company_id"])
        print("Company Name:", drive["company_name"])
        print("Drive Title:", drive["drive_title"])
        print("Drive Date:", drive["drive_date"])
        print("Job Role:", drive["job_role"])
        print("Job Location:", drive["job_location"])
        print("Package (LPA):", drive["package_in_lpa"])
        print("Role Description:", drive["role_description"])
        print("Minimum CGPA:", drive["minimum_cgpa"])
        print("Minimum 10th %:", drive["minimum_10th_percentage"])
        print("Minimum 12th %:", drive["minimum_12th_percentage"])
        print("Maximum Backlogs:", drive["maximum_backlogs"])
        print("Eligible Degree:", drive["eligible_degree"])
        print("Eligible Branch:", drive["eligible_branch"])
        print("Application Deadline:", drive["application_deadline"])
        print("Created By:", drive["created_by"])
        print("Created At:", drive["created_at"])
        print("Drive Status:", drive["drive_status"])

        cursor.close()
        connection.close()



    def add_placement_drive(self, user):

        connection = create_connection()
        cursor = connection.cursor()

        print("\n================================")
        print("      ADD PLACEMENT DRIVE")
        print("================================")

        # Show available companies
        cursor.execute("""
            SELECT
                company_id,
                company_name
            FROM company
            ORDER BY company_name
        """)

        companies = cursor.fetchall()

        if not companies:
            print("\nNo companies found.")
            print("Please add a company first.")

            cursor.close()
            connection.close()

            return

        print("\nAvailable Companies")
        print("--------------------------------")

        for company in companies:
            print(
                "Company ID:",
                company[0],
                "| Company Name:",
                company[1]
            )

        company_id = input("\nCompany ID: ")

        if not company_id.isdigit():
            print("\nInvalid Company ID.")

            cursor.close()
            connection.close()

            return

        company_id = int(company_id)

        # Verify company exists
        cursor.execute(
            """
            SELECT company_id
            FROM company
            WHERE company_id = %s
            """,
            (company_id,)
        )

        company = cursor.fetchone()

        if company is None:
            print("\nCompany not found.")

            cursor.close()
            connection.close()

            return

        drive_title = input("Drive Title: ")
        drive_date = input("Drive Date (YYYY-MM-DD): ")
        job_role = input("Job Role: ")
        job_location = input("Job Location: ")
        package_in_lpa = input("Package (LPA): ")
        role_description = input("Role Description: ")
        minimum_cgpa = input("Minimum CGPA: ")
        minimum_10th_percentage = input("Minimum 10th Percentage: ")
        minimum_12th_percentage = input("Minimum 12th Percentage: ")
        maximum_backlogs = input("Maximum Backlogs: ")
        eligible_degree = input("Eligible Degree: ")
        eligible_branch = input("Eligible Branch: ")
        application_deadline = input(
            "Application Deadline (YYYY-MM-DD): "
        )

        print("\nDrive Status")
        print("1. UPCOMING")
        print("2. OPEN")
        print("3. CLOSED")
        print("4. CANCELLED")

        status_choice = input("Select Status: ")

        status_map = {
            "1": "UPCOMING",
            "2": "OPEN",
            "3": "CLOSED",
            "4": "CANCELLED"
        }

        drive_status = status_map.get(status_choice)

        if drive_status is None:
            print("\nInvalid drive status.")

            cursor.close()
            connection.close()

            return

        # Basic required-field validation
        if not drive_title.strip():
            print("\nDrive title is required.")

            cursor.close()
            connection.close()

            return

        if not drive_date.strip():
            print("\nDrive date is required.")

            cursor.close()
            connection.close()

            return

        if not job_role.strip():
            print("\nJob role is required.")

            cursor.close()
            connection.close()

            return

        if not job_location.strip():
            print("\nJob location is required.")

            cursor.close()
            connection.close()

            return

        if not package_in_lpa.strip():
            print("\nPackage is required.")

            cursor.close()
            connection.close()

            return

        try:

            package_in_lpa = float(package_in_lpa)

            minimum_cgpa = (
                float(minimum_cgpa)
                if minimum_cgpa.strip()
                else None
            )

            minimum_10th_percentage = (
                float(minimum_10th_percentage)
                if minimum_10th_percentage.strip()
                else None
            )

            minimum_12th_percentage = (
                float(minimum_12th_percentage)
                if minimum_12th_percentage.strip()
                else None
            )

            maximum_backlogs = (
                int(maximum_backlogs)
                if maximum_backlogs.strip()
                else 0
            )

        except ValueError:

            print("\nInvalid numeric value entered.")

            cursor.close()
            connection.close()

            return

        insert_query = """
            INSERT INTO drive (
                company_id,
                drive_title,
                drive_date,
                job_role,
                job_location,
                package_in_lpa,
                role_description,
                minimum_cgpa,
                minimum_10th_percentage,
                minimum_12th_percentage,
                maximum_backlogs,
                eligible_degree,
                eligible_branch,
                application_deadline,
                created_by,
                drive_status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        values = (
            company_id,
            drive_title,
            drive_date,
            job_role,
            job_location,
            package_in_lpa,
            role_description if role_description.strip() else None,
            minimum_cgpa,
            minimum_10th_percentage,
            minimum_12th_percentage,
            maximum_backlogs,
            eligible_degree if eligible_degree.strip() else None,
            eligible_branch if eligible_branch.strip() else None,
            application_deadline if application_deadline.strip() else None,
            user.user_id,
            drive_status
        )

        try:

            cursor.execute(insert_query, values)

            connection.commit()

            print("\n================================")
            print("Placement drive added successfully.")
            print("Drive ID:", cursor.lastrowid)
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to add placement drive.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()


    def update_placement_drive(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("     UPDATE PLACEMENT DRIVE")
        print("================================")

        drive_id = input("Enter Drive ID: ")

        if not drive_id.isdigit():
            print("\nInvalid Drive ID.")

            cursor.close()
            connection.close()

            return

        drive_id = int(drive_id)

        query = """
            SELECT
                drive_id,
                company_id,
                drive_title,
                drive_date,
                job_role,
                job_location,
                package_in_lpa,
                role_description,
                minimum_cgpa,
                minimum_10th_percentage,
                minimum_12th_percentage,
                maximum_backlogs,
                eligible_degree,
                eligible_branch,
                application_deadline,
                drive_status
            FROM drive
            WHERE drive_id = %s
        """

        cursor.execute(query, (drive_id,))
        drive = cursor.fetchone()

        if drive is None:
            print("\nPlacement drive not found.")

            cursor.close()
            connection.close()

            return

        print("\nCurrent Placement Drive Details")
        print("--------------------------------")
        print("Company ID:", drive["company_id"])
        print("Drive Title:", drive["drive_title"])
        print("Drive Date:", drive["drive_date"])
        print("Job Role:", drive["job_role"])
        print("Job Location:", drive["job_location"])
        print("Package (LPA):", drive["package_in_lpa"])
        print("Role Description:", drive["role_description"])
        print("Minimum CGPA:", drive["minimum_cgpa"])
        print("Minimum 10th %:", drive["minimum_10th_percentage"])
        print("Minimum 12th %:", drive["minimum_12th_percentage"])
        print("Maximum Backlogs:", drive["maximum_backlogs"])
        print("Eligible Degree:", drive["eligible_degree"])
        print("Eligible Branch:", drive["eligible_branch"])
        print("Application Deadline:", drive["application_deadline"])
        print("Drive Status:", drive["drive_status"])

        print("\nEnter new details.")
        print("Press Enter to keep the existing value.")

        company_id = input("Company ID: ")
        drive_title = input("Drive Title: ")
        drive_date = input("Drive Date (YYYY-MM-DD): ")
        job_role = input("Job Role: ")
        job_location = input("Job Location: ")
        package_in_lpa = input("Package (LPA): ")
        role_description = input("Role Description: ")
        minimum_cgpa = input("Minimum CGPA: ")
        minimum_10th_percentage = input("Minimum 10th Percentage: ")
        minimum_12th_percentage = input("Minimum 12th Percentage: ")
        maximum_backlogs = input("Maximum Backlogs: ")
        eligible_degree = input("Eligible Degree: ")
        eligible_branch = input("Eligible Branch: ")
        application_deadline = input(
            "Application Deadline (YYYY-MM-DD): "
        )

        print("\nDrive Status")
        print("1. UPCOMING")
        print("2. OPEN")
        print("3. CLOSED")
        print("4. CANCELLED")

        status_choice = input("Select Status: ")

        # Keep existing status if Enter is pressed
        if status_choice.strip() == "":
            drive_status = drive["drive_status"]

        else:

            status_map = {
                "1": "UPCOMING",
                "2": "OPEN",
                "3": "CLOSED",
                "4": "CANCELLED"
            }

            drive_status = status_map.get(status_choice)

            if drive_status is None:
                print("\nInvalid drive status.")

                cursor.close()
                connection.close()

                return

        # Keep existing values when input is blank
        if company_id.strip():
            if not company_id.isdigit():
                print("\nInvalid Company ID.")

                cursor.close()
                connection.close()

                return

            company_id = int(company_id)

            cursor.execute(
                """
                SELECT company_id
                FROM company
                WHERE company_id = %s
                """,
                (company_id,)
            )

            company = cursor.fetchone()

            if company is None:
                print("\nCompany not found.")

                cursor.close()
                connection.close()

                return

        else:
            company_id = drive["company_id"]

        drive_title = (
            drive_title
            if drive_title.strip()
            else drive["drive_title"]
        )

        drive_date = (
            drive_date
            if drive_date.strip()
            else drive["drive_date"]
        )

        job_role = (
            job_role
            if job_role.strip()
            else drive["job_role"]
        )

        job_location = (
            job_location
            if job_location.strip()
            else drive["job_location"]
        )

        role_description = (
            role_description
            if role_description.strip()
            else drive["role_description"]
        )

        eligible_degree = (
            eligible_degree
            if eligible_degree.strip()
            else drive["eligible_degree"]
        )

        eligible_branch = (
            eligible_branch
            if eligible_branch.strip()
            else drive["eligible_branch"]
        )

        application_deadline = (
            application_deadline
            if application_deadline.strip()
            else drive["application_deadline"]
        )

        try:

            package_in_lpa = (
                float(package_in_lpa)
                if package_in_lpa.strip()
                else drive["package_in_lpa"]
            )

            minimum_cgpa = (
                float(minimum_cgpa)
                if minimum_cgpa.strip()
                else drive["minimum_cgpa"]
            )

            minimum_10th_percentage = (
                float(minimum_10th_percentage)
                if minimum_10th_percentage.strip()
                else drive["minimum_10th_percentage"]
            )

            minimum_12th_percentage = (
                float(minimum_12th_percentage)
                if minimum_12th_percentage.strip()
                else drive["minimum_12th_percentage"]
            )

            maximum_backlogs = (
                int(maximum_backlogs)
                if maximum_backlogs.strip()
                else drive["maximum_backlogs"]
            )

        except ValueError:

            print("\nInvalid numeric value entered.")

            cursor.close()
            connection.close()

            return

        update_query = """
            UPDATE drive
            SET
                company_id = %s,
                drive_title = %s,
                drive_date = %s,
                job_role = %s,
                job_location = %s,
                package_in_lpa = %s,
                role_description = %s,
                minimum_cgpa = %s,
                minimum_10th_percentage = %s,
                minimum_12th_percentage = %s,
                maximum_backlogs = %s,
                eligible_degree = %s,
                eligible_branch = %s,
                application_deadline = %s,
                drive_status = %s
            WHERE drive_id = %s
        """

        values = (
            company_id,
            drive_title,
            drive_date,
            job_role,
            job_location,
            package_in_lpa,
            role_description,
            minimum_cgpa,
            minimum_10th_percentage,
            minimum_12th_percentage,
            maximum_backlogs,
            eligible_degree,
            eligible_branch,
            application_deadline,
            drive_status,
            drive_id
        )

        try:

            cursor.execute(update_query, values)

            connection.commit()

            print("\n================================")
            print("Placement drive updated successfully.")
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to update placement drive.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()




    def delete_placement_drive(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("     DELETE PLACEMENT DRIVE")
        print("================================")

        drive_id = input("Enter Drive ID: ")

        if not drive_id.isdigit():
            print("\nInvalid Drive ID.")

            cursor.close()
            connection.close()

            return

        drive_id = int(drive_id)

        query = """
            SELECT
                d.drive_id,
                d.drive_title,
                d.drive_date,
                d.job_role,
                d.drive_status,
                c.company_name
            FROM drive d
            INNER JOIN company c
                ON d.company_id = c.company_id
            WHERE d.drive_id = %s
        """

        cursor.execute(query, (drive_id,))
        drive = cursor.fetchone()

        if drive is None:
            print("\nPlacement drive not found.")

            cursor.close()
            connection.close()

            return

        print("\nPlacement Drive Found")
        print("--------------------------------")
        print("Drive ID:", drive["drive_id"])
        print("Company:", drive["company_name"])
        print("Drive Title:", drive["drive_title"])
        print("Drive Date:", drive["drive_date"])
        print("Job Role:", drive["job_role"])
        print("Drive Status:", drive["drive_status"])

        # Check whether students have applied
        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM student_application
            WHERE drive_id = %s
            """,
            (drive_id,)
        )

        application_data = cursor.fetchone()

        application_count = application_data["total"]

        if application_count > 0:

            print("\nCannot delete this placement drive.")
            print(
                "There are",
                application_count,
                "student application(s) linked to this drive."
            )
            print(
                "Remove or handle the applications first."
            )

            cursor.close()
            connection.close()

            return

        confirmation = input(
            "\nAre you sure you want to delete this placement drive? (YES/NO): "
        )

        if confirmation.strip().upper() != "YES":

            print("\nDeletion cancelled.")

            cursor.close()
            connection.close()

            return

        try:

            cursor.execute(
                """
                DELETE FROM drive
                WHERE drive_id = %s
                """,
                (drive_id,)
            )

            connection.commit()

            print("\n================================")
            print("Placement drive deleted successfully.")
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nCannot delete this placement drive.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()



    def manage_student_applications(self):

        while True:

            print("\n================================")
            print("   MANAGE STUDENT APPLICATIONS")
            print("================================")

            print("1. View All Applications")
            print("2. View Application Details")
            print("3. Update Application Status")
            print("4. Delete Application")
            print("5. Back")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_all_student_applications()

            elif choice == "2":
                self.view_student_application_details()

            elif choice == "3":
                self.update_student_application_status()

            elif choice == "4":
                self.delete_student_application()

            elif choice == "5":
                break

            else:
                print("\nInvalid choice.")


    def view_all_student_applications(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("      ALL STUDENT APPLICATIONS")
        print("================================")

        query = """
            SELECT
                sa.application_id,
                sa.student_id,
                u.first_name,
                u.middle_name,
                u.last_name,
                d.drive_title,
                c.company_name,
                sa.status
            FROM student_application sa

            INNER JOIN student s
                ON sa.student_id = s.student_id

            INNER JOIN users u
                ON s.user_id = u.user_id

            INNER JOIN drive d
                ON sa.drive_id = d.drive_id

            INNER JOIN company c
                ON d.company_id = c.company_id

            ORDER BY sa.application_id DESC
        """

        try:

            cursor.execute(query)

            applications = cursor.fetchall()

            if not applications:

                print("\nNo student applications found.")

                return

            for application in applications:

                full_name = " ".join(
                    part
                    for part in [
                        application["first_name"],
                        application["middle_name"],
                        application["last_name"]
                    ]
                    if part
                )

                print("\n--------------------------------")
                print(
                    "Application ID:",
                    application["application_id"]
                )
                print(
                    "Student ID:",
                    application["student_id"]
                )
                print(
                    "Student Name:",
                    full_name
                )
                print(
                    "Drive:",
                    application["drive_title"]
                )
                print(
                    "Company:",
                    application["company_name"]
                )
                print(
                    "Status:",
                    application["status"]
                )

        except Exception as e:

            print("\nFailed to load applications.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()



    def view_student_application_details(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       APPLICATION DETAILS")
        print("================================")

        application_id = input("Enter Application ID: ")

        if not application_id.isdigit():

            print("\nInvalid Application ID.")

            cursor.close()
            connection.close()

            return

        application_id = int(application_id)

        query = """
            SELECT
                sa.application_id,
                sa.student_id,

                u.user_id,
                u.first_name,
                u.middle_name,
                u.last_name,
                u.email,
                u.phone,
                u.role,
                u.status AS user_status,

                d.drive_id,
                d.drive_title,
                d.drive_date,
                d.job_role,
                d.job_location,
                d.package_in_lpa,
                d.role_description,
                d.minimum_cgpa,
                d.minimum_10th_percentage,
                d.minimum_12th_percentage,
                d.maximum_backlogs,
                d.eligible_degree,
                d.eligible_branch,
                d.application_deadline,
                d.drive_status,

                c.company_id,
                c.company_name,
                c.industry_type,
                c.company_description,
                c.location AS company_location,
                c.website,
                c.contact_email,
                c.contact_phone,

                sa.status AS application_status,
                sa.remarks,
                sa.applied_at,
                sa.updated_at

            FROM student_application sa

            INNER JOIN student s
                ON sa.student_id = s.student_id

            INNER JOIN users u
                ON s.user_id = u.user_id

            INNER JOIN drive d
                ON sa.drive_id = d.drive_id

            INNER JOIN company c
                ON d.company_id = c.company_id

            WHERE sa.application_id = %s
        """

        try:

            cursor.execute(query, (application_id,))

            application = cursor.fetchone()

            if application is None:

                print("\nApplication not found.")

                return

            full_name = " ".join(
                part
                for part in [
                    application["first_name"],
                    application["middle_name"],
                    application["last_name"]
                ]
                if part
            )

            print("\n================================")
            print("       APPLICATION DETAILS")
            print("================================")

            print("\nAPPLICATION")
            print("--------------------------------")
            print("Application ID:", application["application_id"])
            print("Application Status:", application["application_status"])
            print("Remarks:", application["remarks"])
            print("Applied At:", application["applied_at"])
            print("Updated At:", application["updated_at"])

            print("\nSTUDENT INFORMATION")
            print("--------------------------------")
            print("User ID:", application["user_id"])
            print("Student ID:", application["student_id"])
            print("Student Name:", full_name)
            print("Email:", application["email"])
            print("Phone:", application["phone"])
            print("Role:", application["role"])
            print("Account Status:", application["user_status"])

            print("\nPLACEMENT DRIVE")
            print("--------------------------------")
            print("Drive ID:", application["drive_id"])
            print("Drive Title:", application["drive_title"])
            print("Drive Date:", application["drive_date"])
            print("Job Role:", application["job_role"])
            print("Job Location:", application["job_location"])
            print("Package (LPA):", application["package_in_lpa"])
            print("Role Description:", application["role_description"])
            print("Minimum CGPA:", application["minimum_cgpa"])
            print("Minimum 10th %:", application["minimum_10th_percentage"])
            print("Minimum 12th %:", application["minimum_12th_percentage"])
            print("Maximum Backlogs:", application["maximum_backlogs"])
            print("Eligible Degree:", application["eligible_degree"])
            print("Eligible Branch:", application["eligible_branch"])
            print("Application Deadline:", application["application_deadline"])
            print("Drive Status:", application["drive_status"])

            print("\nCOMPANY INFORMATION")
            print("--------------------------------")
            print("Company ID:", application["company_id"])
            print("Company Name:", application["company_name"])
            print("Industry Type:", application["industry_type"])
            print("Description:", application["company_description"])
            print("Location:", application["company_location"])
            print("Website:", application["website"])
            print("Contact Email:", application["contact_email"])
            print("Contact Phone:", application["contact_phone"])

        except Exception as e:

            print("\nFailed to load application details.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()




    def update_student_application_status(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("   UPDATE APPLICATION STATUS")
        print("================================")

        application_id = input("Enter Application ID: ")

        if not application_id.isdigit():

            print("\nInvalid Application ID.")

            cursor.close()
            connection.close()

            return

        application_id = int(application_id)

        query = """
            SELECT
                sa.application_id,
                sa.status,
                sa.remarks,

                u.first_name,
                u.middle_name,
                u.last_name,

                d.drive_title,

                c.company_name

            FROM student_application sa

            INNER JOIN student s
                ON sa.student_id = s.student_id

            INNER JOIN users u
                ON s.user_id = u.user_id

            INNER JOIN drive d
                ON sa.drive_id = d.drive_id

            INNER JOIN company c
                ON d.company_id = c.company_id

            WHERE sa.application_id = %s
        """

        try:

            cursor.execute(query, (application_id,))

            application = cursor.fetchone()

            if application is None:

                print("\nApplication not found.")

                return

            full_name = " ".join(
                part
                for part in [
                    application["first_name"],
                    application["middle_name"],
                    application["last_name"]
                ]
                if part
            )

            print("\nCURRENT APPLICATION")
            print("--------------------------------")
            print("Application ID:", application["application_id"])
            print("Student:", full_name)
            print("Company:", application["company_name"])
            print("Drive:", application["drive_title"])
            print("Current Status:", application["status"])
            print("Current Remarks:", application["remarks"])

            print("\nSELECT NEW STATUS")
            print("--------------------------------")
            print("1. APPLIED")
            print("2. SHORTLISTED")
            print("3. REJECTED")
            print("4. SELECTED")

            status_choice = input("\nEnter choice: ")

            status_map = {
                "1": "APPLIED",
                "2": "SHORTLISTED",
                "3": "REJECTED",
                "4": "SELECTED"
            }

            new_status = status_map.get(status_choice)

            if new_status is None:

                print("\nInvalid status.")

                return

            remarks = input("Remarks: ")

            if not remarks.strip():

                remarks = application["remarks"]

            update_query = """
                UPDATE student_application
                SET
                    status = %s,
                    remarks = %s
                WHERE application_id = %s
            """

            cursor.execute(
                update_query,
                (
                    new_status,
                    remarks,
                    application_id
                )
            )

            connection.commit()

            print("\n================================")
            print("Application status updated successfully.")
            print("New Status:", new_status)
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to update application status.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()




    def delete_student_application(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       DELETE APPLICATION")
        print("================================")

        application_id = input("Enter Application ID: ")

        if not application_id.isdigit():

            print("\nInvalid Application ID.")

            cursor.close()
            connection.close()

            return

        application_id = int(application_id)

        query = """
            SELECT
                sa.application_id,
                sa.status,

                u.first_name,
                u.middle_name,
                u.last_name,

                d.drive_title,

                c.company_name

            FROM student_application sa

            INNER JOIN student s
                ON sa.student_id = s.student_id

            INNER JOIN users u
                ON s.user_id = u.user_id

            INNER JOIN drive d
                ON sa.drive_id = d.drive_id

            INNER JOIN company c
                ON d.company_id = c.company_id

            WHERE sa.application_id = %s
        """

        try:

            cursor.execute(query, (application_id,))

            application = cursor.fetchone()

            if application is None:

                print("\nApplication not found.")

                return

            full_name = " ".join(
                part
                for part in [
                    application["first_name"],
                    application["middle_name"],
                    application["last_name"]
                ]
                if part
            )

            print("\nAPPLICATION FOUND")
            print("--------------------------------")
            print("Application ID:", application["application_id"])
            print("Student:", full_name)
            print("Company:", application["company_name"])
            print("Drive:", application["drive_title"])
            print("Status:", application["status"])

            confirmation = input(
                "\nAre you sure you want to delete this application? (YES/NO): "
            )

            if confirmation.strip().upper() != "YES":

                print("\nDeletion cancelled.")

                return

            delete_query = """
                DELETE FROM student_application
                WHERE application_id = %s
            """

            cursor.execute(
                delete_query,
                (application_id,)
            )

            connection.commit()

            print("\n================================")
            print("Student application deleted successfully.")
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to delete application.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()



    def manage_placement_news(self, user):

        while True:

            print("\n================================")
            print("      MANAGE PLACEMENT NEWS")
            print("================================")

            print("1. View All Placement News")
            print("2. View Placement News Details")
            print("3. Add Placement News")
            print("4. Update Placement News")
            print("5. Delete Placement News")
            print("6. Back")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_all_placement_news()

            elif choice == "2":
                self.view_placement_news_details()

            elif choice == "3":
                self.add_placement_news(user)

            elif choice == "4":
                self.update_placement_news()

            elif choice == "5":
                self.delete_placement_news()

            elif choice == "6":
                break

            else:
                print("\nInvalid choice.")



    def view_all_placement_news(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       ALL PLACEMENT NEWS")
        print("================================")

        query = """
            SELECT
                pn.news_id,
                pn.title,
                pn.news_description,
                pn.company_id,
                c.company_name,
                pn.drive_id,
                d.drive_title,
                pn.published_by,
                u.first_name,
                u.middle_name,
                u.last_name,
                pn.target_role,
                pn.published_date,
                pn.valid_till,
                pn.is_active,
                pn.created_at
            FROM placement_news pn
            LEFT JOIN company c
                ON pn.company_id = c.company_id
            LEFT JOIN drive d
                ON pn.drive_id = d.drive_id
            LEFT JOIN users u
                ON pn.published_by = u.user_id
            ORDER BY pn.news_id DESC
        """

        try:
            cursor.execute(query)
            news_list = cursor.fetchall()

            if not news_list:
                print("\nNo placement news found.")
                return

            for news in news_list:

                publisher_name = " ".join(
                    part
                    for part in [
                        news["first_name"],
                        news["middle_name"],
                        news["last_name"]
                    ]
                    if part
                )

                print("\n--------------------------------")
                print("News ID:", news["news_id"])
                print("Title:", news["title"])
                print("Description:", news["news_description"])
                print("Company ID:", news["company_id"] or "N/A")
                print("Company:", news["company_name"] or "N/A")
                print("Drive ID:", news["drive_id"] or "N/A")
                print("Drive:", news["drive_title"] or "N/A")
                print("Published By:", news["published_by"])
                print(
                    "Publisher Name:",
                    publisher_name if publisher_name else "N/A"
                )
                print("Target Role:", news["target_role"])
                print("Published Date:", news["published_date"])
                print("Valid Till:", news["valid_till"] or "N/A")
                print(
                    "Active:",
                    "YES" if news["is_active"] else "NO"
                )
                print("Created At:", news["created_at"])

        except Exception as e:
            print("\nFailed to load placement news.")
            print("Error:", e)

        finally:
            cursor.close()
            connection.close()



    def view_placement_news_details(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("     PLACEMENT NEWS DETAILS")
        print("================================")

        news_id = input("Enter News ID: ")

        if not news_id.isdigit():
            print("\nInvalid News ID.")
            cursor.close()
            connection.close()
            return

        news_id = int(news_id)

        query = """
            SELECT
                pn.news_id,
                pn.title,
                pn.news_description,
                pn.company_id,
                c.company_name,
                pn.drive_id,
                d.drive_title,
                pn.published_by,
                u.first_name,
                u.middle_name,
                u.last_name,
                pn.target_role,
                pn.published_date,
                pn.valid_till,
                pn.is_active,
                pn.created_at
            FROM placement_news pn
            LEFT JOIN company c
                ON pn.company_id = c.company_id
            LEFT JOIN drive d
                ON pn.drive_id = d.drive_id
            LEFT JOIN users u
                ON pn.published_by = u.user_id
            WHERE pn.news_id = %s
        """

        try:
            cursor.execute(query, (news_id,))
            news = cursor.fetchone()

            if news is None:
                print("\nPlacement news not found.")
                return

            publisher_name = " ".join(
                part
                for part in [
                    news["first_name"],
                    news["middle_name"],
                    news["last_name"]
                ]
                if part
            )

            print("\n================================")
            print("     PLACEMENT NEWS DETAILS")
            print("================================")

            print("\nNEWS INFORMATION")
            print("--------------------------------")
            print("News ID:", news["news_id"])
            print("Title:", news["title"])
            print("Description:", news["news_description"])

            print("\nCOMPANY INFORMATION")
            print("--------------------------------")
            print("Company ID:", news["company_id"] or "N/A")
            print("Company Name:", news["company_name"] or "N/A")

            print("\nPLACEMENT DRIVE INFORMATION")
            print("--------------------------------")
            print("Drive ID:", news["drive_id"] or "N/A")
            print("Drive Title:", news["drive_title"] or "N/A")

            print("\nPUBLISHING INFORMATION")
            print("--------------------------------")
            print("Published By User ID:", news["published_by"])
            print(
                "Publisher Name:",
                publisher_name if publisher_name else "N/A"
            )
            print("Target Role:", news["target_role"])
            print("Published Date:", news["published_date"])
            print("Valid Till:", news["valid_till"] or "N/A")
            print(
                "Active:",
                "YES" if news["is_active"] else "NO"
            )
            print("Created At:", news["created_at"])

        except Exception as e:
            print("\nFailed to load placement news details.")
            print("Error:", e)

        finally:
            cursor.close()
            connection.close()



    def add_placement_news(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       ADD PLACEMENT NEWS")
        print("================================")

        try:

            # -----------------------------
            # NEWS TITLE
            # -----------------------------
            title = input("Enter News Title: ")

            if not title.strip():
                print("\nNews title cannot be empty.")
                return

            # -----------------------------
            # NEWS DESCRIPTION
            # -----------------------------
            news_description = input("Enter News Description: ")

            if not news_description.strip():
                print("\nNews description cannot be empty.")
                return

            # -----------------------------
            # COMPANY
            # -----------------------------
            print("\nAvailable Companies")
            print("--------------------------------")

            cursor.execute("""
                SELECT
                    company_id,
                    company_name
                FROM company
                ORDER BY company_id
            """)

            companies = cursor.fetchall()

            if companies:
                for company in companies:
                    print(
                        company["company_id"],
                        "-",
                        company["company_name"]
                    )
            else:
                print("No companies found.")

            company_id_input = input(
                "\nEnter Company ID (press Enter for none): "
            )

            if company_id_input.strip():

                if not company_id_input.isdigit():
                    print("\nInvalid Company ID.")
                    return

                company_id = int(company_id_input)

                cursor.execute(
                    """
                    SELECT company_id
                    FROM company
                    WHERE company_id = %s
                    """,
                    (company_id,)
                )

                company = cursor.fetchone()

                if company is None:
                    print("\nCompany not found.")
                    return

            else:
                company_id = None

            # -----------------------------
            # PLACEMENT DRIVE
            # -----------------------------
            print("\nAvailable Placement Drives")
            print("--------------------------------")

            cursor.execute("""
                SELECT
                    d.drive_id,
                    d.drive_title,
                    c.company_name
                FROM drive d
                INNER JOIN company c
                    ON d.company_id = c.company_id
                ORDER BY d.drive_id
            """)

            drives = cursor.fetchall()

            if drives:
                for drive in drives:
                    print(
                        drive["drive_id"],
                        "-",
                        drive["drive_title"],
                        "(",
                        drive["company_name"],
                        ")"
                    )
            else:
                print("No placement drives found.")

            drive_id_input = input(
                "\nEnter Drive ID (press Enter for none): "
            )

            if drive_id_input.strip():

                if not drive_id_input.isdigit():
                    print("\nInvalid Drive ID.")
                    return

                drive_id = int(drive_id_input)

                cursor.execute(
                    """
                    SELECT
                        drive_id,
                        company_id
                    FROM drive
                    WHERE drive_id = %s
                    """,
                    (drive_id,)
                )

                drive = cursor.fetchone()

                if drive is None:
                    print("\nPlacement drive not found.")
                    return

                # If both company and drive are selected,
                # make sure they belong together.
                if company_id is not None:

                    if drive["company_id"] != company_id:
                        print(
                            "\nSelected drive does not belong "
                            "to the selected company."
                        )
                        return

            else:
                drive_id = None

            # -----------------------------
            # TARGET ROLE
            # -----------------------------
            print("\nTarget Role")
            print("--------------------------------")
            print("1. STUDENT")
            print("2. FACULTY")
            print("3. ADMIN")
            print("4. ALL")

            target_choice = input("\nEnter choice: ")

            target_role_map = {
                "1": "STUDENT",
                "2": "FACULTY",
                "3": "ADMIN",
                "4": "ALL"
            }

            target_role = target_role_map.get(target_choice)

            if target_role is None:
                print("\nInvalid target role.")
                return

            # -----------------------------
            # PUBLISHED DATE
            # -----------------------------
            published_date = input(
                "Enter Published Date (YYYY-MM-DD): "
            )

            if not published_date.strip():
                print("\nPublished date cannot be empty.")
                return

            # -----------------------------
            # VALID TILL
            # -----------------------------
            valid_till = input(
                "Enter Valid Till (YYYY-MM-DD, press Enter for none): "
            )

            if not valid_till.strip():
                valid_till = None

            # -----------------------------
            # ACTIVE STATUS
            # -----------------------------
            is_active_input = input(
                "Is Active? (YES/NO, default YES): "
            )

            if not is_active_input.strip():

                is_active = 1

            elif is_active_input.strip().upper() == "YES":

                is_active = 1

            elif is_active_input.strip().upper() == "NO":

                is_active = 0

            else:
                print("\nInvalid active status.")
                return

            # -----------------------------
            # INSERT NEWS
            # -----------------------------
            query = """
                INSERT INTO placement_news (
                    title,
                    news_description,
                    company_id,
                    drive_id,
                    published_by,
                    target_role,
                    published_date,
                    valid_till,
                    is_active
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    title,
                    news_description,
                    company_id,
                    drive_id,
                    user.user_id,
                    target_role,
                    published_date,
                    valid_till,
                    is_active
                )
            )

            connection.commit()

            print("\n================================")
            print("Placement news added successfully.")
            print("News ID:", cursor.lastrowid)
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to add placement news.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()



    def update_placement_news(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("      UPDATE PLACEMENT NEWS")
        print("================================")

        news_id = input("Enter News ID: ")

        if not news_id.isdigit():
            print("\nInvalid News ID.")
            cursor.close()
            connection.close()
            return

        news_id = int(news_id)

        try:

            # --------------------------------
            # FIND EXISTING NEWS
            # --------------------------------
            cursor.execute(
                """
                SELECT *
                FROM placement_news
                WHERE news_id = %s
                """,
                (news_id,)
            )

            news = cursor.fetchone()

            if news is None:
                print("\nPlacement news not found.")
                return

            # --------------------------------
            # SHOW CURRENT INFORMATION
            # --------------------------------
            print("\nCurrent Placement News")
            print("--------------------------------")
            print("News ID:", news["news_id"])
            print("Title:", news["title"])
            print("Description:", news["news_description"])
            print("Company ID:", news["company_id"] or "N/A")
            print("Drive ID:", news["drive_id"] or "N/A")
            print("Published By:", news["published_by"])
            print("Target Role:", news["target_role"])
            print("Published Date:", news["published_date"])
            print("Valid Till:", news["valid_till"] or "N/A")
            print(
                "Active:",
                "YES" if news["is_active"] else "NO"
            )

            print("\nPress Enter to keep the current value.")

            # --------------------------------
            # TITLE
            # --------------------------------
            title = input(
                f"Title [{news['title']}]: "
            )

            if not title.strip():
                title = news["title"]

            # --------------------------------
            # DESCRIPTION
            # --------------------------------
            news_description = input(
                f"Description [{news['news_description']}]: "
            )

            if not news_description.strip():
                news_description = news["news_description"]

            # --------------------------------
            # COMPANY
            # --------------------------------
            print("\nAvailable Companies")
            print("--------------------------------")

            cursor.execute(
                """
                SELECT
                    company_id,
                    company_name
                FROM company
                ORDER BY company_id
                """
            )

            companies = cursor.fetchall()

            if companies:
                for company in companies:
                    print(
                        company["company_id"],
                        "-",
                        company["company_name"]
                    )
            else:
                print("No companies found.")

            company_id_input = input(
                f"\nCompany ID "
                f"[{news['company_id'] if news['company_id'] else 'None'}]: "
            )

            if not company_id_input.strip():

                company_id = news["company_id"]

            elif company_id_input.isdigit():

                company_id = int(company_id_input)

                cursor.execute(
                    """
                    SELECT company_id
                    FROM company
                    WHERE company_id = %s
                    """,
                    (company_id,)
                )

                company = cursor.fetchone()

                if company is None:
                    print("\nCompany not found.")
                    return

            else:

                print("\nInvalid Company ID.")
                return

            # --------------------------------
            # PLACEMENT DRIVE
            # --------------------------------
            print("\nAvailable Placement Drives")
            print("--------------------------------")

            cursor.execute(
                """
                SELECT
                    d.drive_id,
                    d.drive_title,
                    c.company_name
                FROM drive d
                INNER JOIN company c
                    ON d.company_id = c.company_id
                ORDER BY d.drive_id
                """
            )

            drives = cursor.fetchall()

            if drives:
                for drive in drives:
                    print(
                        drive["drive_id"],
                        "-",
                        drive["drive_title"],
                        "(",
                        drive["company_name"],
                        ")"
                    )
            else:
                print("No placement drives found.")

            drive_id_input = input(
                f"\nDrive ID "
                f"[{news['drive_id'] if news['drive_id'] else 'None'}]: "
            )

            if not drive_id_input.strip():

                drive_id = news["drive_id"]

            elif drive_id_input.isdigit():

                drive_id = int(drive_id_input)

                cursor.execute(
                    """
                    SELECT
                        drive_id,
                        company_id
                    FROM drive
                    WHERE drive_id = %s
                    """,
                    (drive_id,)
                )

                drive = cursor.fetchone()

                if drive is None:
                    print("\nPlacement drive not found.")
                    return

                # Make sure selected drive belongs
                # to selected company.
                if company_id is not None:

                    if drive["company_id"] != company_id:
                        print(
                            "\nSelected drive does not belong "
                            "to the selected company."
                        )
                        return

            else:

                print("\nInvalid Drive ID.")
                return

            # --------------------------------
            # TARGET ROLE
            # --------------------------------
            print("\nTarget Role")
            print("--------------------------------")
            print("1. STUDENT")
            print("2. FACULTY")
            print("3. ADMIN")
            print("4. ALL")

            target_choice = input(
                f"Enter choice "
                f"[Current: {news['target_role']}]: "
            )

            if not target_choice.strip():

                target_role = news["target_role"]

            else:

                target_role_map = {
                    "1": "STUDENT",
                    "2": "FACULTY",
                    "3": "ADMIN",
                    "4": "ALL"
                }

                target_role = target_role_map.get(target_choice)

                if target_role is None:
                    print("\nInvalid target role.")
                    return

            # --------------------------------
            # PUBLISHED DATE
            # --------------------------------
            published_date = input(
                f"Published Date "
                f"[{news['published_date']}]: "
            )

            if not published_date.strip():
                published_date = news["published_date"]

            # --------------------------------
            # VALID TILL
            # --------------------------------
            valid_till_input = input(
                f"Valid Till "
                f"[{news['valid_till'] if news['valid_till'] else 'None'}]: "
            )

            if not valid_till_input.strip():

                valid_till = news["valid_till"]

            else:

                valid_till = valid_till_input

            # --------------------------------
            # ACTIVE STATUS
            # --------------------------------
            active_input = input(
                f"Active? "
                f"[{'YES' if news['is_active'] else 'NO'}]: "
            )

            if not active_input.strip():

                is_active = news["is_active"]

            elif active_input.strip().upper() == "YES":

                is_active = 1

            elif active_input.strip().upper() == "NO":

                is_active = 0

            else:

                print("\nInvalid active status.")
                return

            # --------------------------------
            # UPDATE DATABASE
            # --------------------------------
            update_query = """
                UPDATE placement_news
                SET
                    title = %s,
                    news_description = %s,
                    company_id = %s,
                    drive_id = %s,
                    target_role = %s,
                    published_date = %s,
                    valid_till = %s,
                    is_active = %s
                WHERE news_id = %s
            """

            cursor.execute(
                update_query,
                (
                    title,
                    news_description,
                    company_id,
                    drive_id,
                    target_role,
                    published_date,
                    valid_till,
                    is_active,
                    news_id
                )
            )

            connection.commit()

            print("\n================================")
            print("Placement news updated successfully.")
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to update placement news.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()



    def delete_placement_news(self):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       DELETE PLACEMENT NEWS")
        print("================================")

        news_id = input("Enter News ID: ")

        if not news_id.isdigit():
            print("\nInvalid News ID.")
            cursor.close()
            connection.close()
            return

        news_id = int(news_id)

        try:

            # --------------------------------
            # FIND NEWS
            # --------------------------------
            query = """
                SELECT
                    pn.news_id,
                    pn.title,
                    pn.news_description,
                    pn.company_id,
                    c.company_name,
                    pn.drive_id,
                    d.drive_title,
                    pn.published_by,
                    pn.target_role,
                    pn.published_date,
                    pn.valid_till,
                    pn.is_active,
                    pn.created_at
                FROM placement_news pn
                LEFT JOIN company c
                    ON pn.company_id = c.company_id
                LEFT JOIN drive d
                    ON pn.drive_id = d.drive_id
                WHERE pn.news_id = %s
            """

            cursor.execute(query, (news_id,))

            news = cursor.fetchone()

            if news is None:
                print("\nPlacement news not found.")
                return

            # --------------------------------
            # DISPLAY NEWS
            # --------------------------------
            print("\nPlacement News Found")
            print("--------------------------------")
            print("News ID:", news["news_id"])
            print("Title:", news["title"])
            print("Description:", news["news_description"])
            print("Company ID:", news["company_id"] or "N/A")
            print("Company:", news["company_name"] or "N/A")
            print("Drive ID:", news["drive_id"] or "N/A")
            print("Drive:", news["drive_title"] or "N/A")
            print("Published By:", news["published_by"])
            print("Target Role:", news["target_role"])
            print("Published Date:", news["published_date"])
            print("Valid Till:", news["valid_till"] or "N/A")
            print(
                "Active:",
                "YES" if news["is_active"] else "NO"
            )
            print("Created At:", news["created_at"])

            # --------------------------------
            # CONFIRMATION
            # --------------------------------
            confirmation = input(
                "\nAre you sure you want to delete "
                "this placement news? (YES/NO): "
            )

            if confirmation.strip().upper() != "YES":

                print("\nDeletion cancelled.")
                return

            # --------------------------------
            # DELETE NEWS
            # --------------------------------
            delete_query = """
                DELETE FROM placement_news
                WHERE news_id = %s
            """

            cursor.execute(
                delete_query,
                (news_id,)
            )

            connection.commit()

            print("\n================================")
            print("Placement news deleted successfully.")
            print("================================")

        except Exception as e:

            connection.rollback()

            print("\nFailed to delete placement news.")
            print("Error:", e)

        finally:

            cursor.close()
            connection.close()





    