from database.connection import create_connection


class StudentService:

    def show_dashboard(self, user):

        while True:

            print("\n================================")
            print("       STUDENT DASHBOARD")
            print("================================")
            print("Welcome,", user.get_full_name())
            print()
            print("1. View Profile")
            print("2. View Attendance")
            print("3. View Marks")
            print("4. View Notices")
            print("5. View Placement Drives")
            print("6. Apply for Placement Drive")
            print("7. Apply for Leave")
            print("8. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.view_profile(user)

            elif choice == "2":
                 self.view_attendance(user)

            elif choice == "3":
                 self.view_marks(user)

            elif choice == "4":
                 self.view_notices(user)

            elif choice == "5":
                 self.view_placement_drives(user)

            elif choice == "6":
               self.apply_for_placement(user)

            elif choice == "7":
                 self.apply_for_leave(user)

            elif choice == "8":
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

                s.student_id,
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

            FROM users u

            INNER JOIN student s
                ON u.user_id = s.user_id

            INNER JOIN department d
                ON s.department_id = d.department_id

            WHERE u.user_id = %s
        """

        cursor.execute(query, (user.user_id,))

        student_data = cursor.fetchone()

        if student_data is None:

            print("\nStudent profile not found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("          STUDENT PROFILE")
        print("================================")

        print("\n--- Account Information ---")
        print("User ID:", student_data["user_id"])
        print("Name:",
              student_data["first_name"],
              student_data["middle_name"] or "",
              student_data["last_name"])
        print("Email:", student_data["email"])
        print("Phone:", student_data["phone"])
        print("Role:", student_data["role"])
        print("Account Status:", student_data["status"])

        print("\n--- Academic Information ---")
        print("Student ID:", student_data["student_id"])
        print("Department:", student_data["department_name"])
        print("Department Code:", student_data["department_code"])
        print("Admission Date:", student_data["admission_date"])
        print("Previous Qualification:",
              student_data["previous_qualification"])
        print("Previous Percentage:",
              student_data["previous_percentage"])
        print("Student Status:",
              student_data["student_status"])

        print("\n--- Personal Information ---")
        print("Date of Birth:", student_data["date_of_birth"])
        print("Gender:", student_data["gender"])
        print("Blood Group:", student_data["blood_group"])
        print("Father Name:", student_data["father_name"])
        print("Mother Name:", student_data["mother_name"])

        print("\n--- Address Information ---")
        print("Address:", student_data["address"])
        print("City:", student_data["city"])
        print("State:", student_data["state"])
        print("Pincode:", student_data["pincode"])
        print("Emergency Contact:",
              student_data["emergency_contact"])

        cursor.close()
        connection.close()


    def view_attendance(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                a.attendance_id,
                a.status,
                a.remarks,
                a.marked_at,
                cs.session_date,
                cs.start_time,
                cs.end_time,
                cs.room_no,
                cs.session_type,
                s.subject_code,
                s.subject_name
            FROM attendance a

            INNER JOIN class_session cs
                ON a.session_id = cs.session_id

            INNER JOIN subject s
                ON cs.subject_id = s.subject_id

            INNER JOIN student st
                ON a.student_id = st.student_id

            WHERE st.user_id = %s

            ORDER BY cs.session_date DESC, cs.start_time DESC
        """

        cursor.execute(query, (user.user_id,))

        attendance_records = cursor.fetchall()

        if not attendance_records:
            print("\nNo attendance records found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("       ATTENDANCE RECORD")
        print("================================")

        for record in attendance_records:

            print("\n--------------------------------")
            print("Subject Code:", record["subject_code"])
            print("Subject Name:", record["subject_name"])
            print("Date:", record["session_date"])
            print("Time:",
                  record["start_time"],
                  "-",
                  record["end_time"])
            print("Room:", record["room_no"])
            print("Session Type:", record["session_type"])
            print("Status:", record["status"])
            print("Remarks:", record["remarks"])

        cursor.close()
        connection.close()

    def view_marks(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                m.marks_id,
                m.cca1,
                m.cca2,
                m.cca3,
                m.midterm,
                m.final_exam,
                m.total_marks,
                m.academic_year,
                m.semester,
                s.subject_code,
                s.subject_name

            FROM marks m

            INNER JOIN student st
                ON m.student_id = st.student_id

            INNER JOIN subject s
                ON m.subject_id = s.subject_id

            WHERE st.user_id = %s

            ORDER BY m.semester, s.subject_code
        """

        cursor.execute(query, (user.user_id,))

        marks_records = cursor.fetchall()

        if not marks_records:
            print("\nNo marks records found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("          STUDENT MARKS")
        print("================================")

        for record in marks_records:

            total = record["total_marks"]

            if total >= 90:
                grade = "A+"
            elif total >= 80:
                grade = "A"
            elif total >= 70:
                grade = "B"
            elif total >= 60:
                grade = "C"
            elif total >= 50:
                grade = "D"
            else:
                grade = "F"

            print("\n--------------------------------")
            print("Subject Code:", record["subject_code"])
            print("Subject Name:", record["subject_name"])
            print("Academic Year:", record["academic_year"])
            print("Semester:", record["semester"])

            print("\nMarks:")
            print("CCA 1:", record["cca1"])
            print("CCA 2:", record["cca2"])
            print("CCA 3:", record["cca3"])
            print("Midterm:", record["midterm"])
            print("Final Exam:", record["final_exam"])

            print("\nTotal Marks:", total)
            print("Grade:", grade)

        cursor.close()
        connection.close()


    def view_notices(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                notice_id,
                title,
                content,
                release_date,
                valid_till,
                target_role
            FROM notice
            WHERE is_active = TRUE
              AND target_role IN ('STUDENT', 'ALL')
              AND release_date <= CURRENT_DATE
              AND (
                  valid_till IS NULL
                  OR valid_till >= CURRENT_DATE
              )
            ORDER BY release_date DESC
        """

        cursor.execute(query)

        notices = cursor.fetchall()

        if not notices:
            print("\nNo active notices found.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("          CAMPUS NOTICES")
        print("================================")

        for notice in notices:

            print("\n--------------------------------")
            print("Notice ID:", notice["notice_id"])
            print("Title:", notice["title"])
            print("Release Date:", notice["release_date"])
            print("Valid Till:", notice["valid_till"])
            print("Target:", notice["target_role"])
            print("\nContent:")
            print(notice["content"])

        cursor.close()
        connection.close()


    def view_placement_drives(self, user):

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
                d.drive_status
            FROM drive d

            INNER JOIN company c
                ON d.company_id = c.company_id

            WHERE d.drive_status IN ('UPCOMING', 'OPEN')

            ORDER BY d.drive_date ASC
        """

        cursor.execute(query)

        drives = cursor.fetchall()

        if not drives:
            print("\nNo placement drives available.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("       PLACEMENT DRIVES")
        print("================================")

        for drive in drives:

            print("\n--------------------------------")
            print("Drive ID:", drive["drive_id"])
            print("Company:", drive["company_name"])
            print("Drive Title:", drive["drive_title"])
            print("Drive Date:", drive["drive_date"])
            print("Job Role:", drive["job_role"])
            print("Location:", drive["job_location"])
            print("Package:", drive["package_in_lpa"], "LPA")
            print("Status:", drive["drive_status"])

            print("\nEligibility:")
            print("Minimum CGPA:", drive["minimum_cgpa"])
            print("Minimum 10th %:", drive["minimum_10th_percentage"])
            print("Minimum 12th %:", drive["minimum_12th_percentage"])
            print("Maximum Backlogs:", drive["maximum_backlogs"])
            print("Eligible Degree:", drive["eligible_degree"])
            print("Eligible Branch:", drive["eligible_branch"])

            print("\nApplication Deadline:",
                  drive["application_deadline"])

            print("\nRole Description:")
            print(drive["role_description"])

        cursor.close()
        connection.close()



    def apply_for_placement(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Find the student's student_id
        student_query = """
            SELECT student_id
            FROM student
            WHERE user_id = %s
        """

        cursor.execute(student_query, (user.user_id,))

        student_data = cursor.fetchone()

        if student_data is None:
            print("\nStudent profile not found.")

            cursor.close()
            connection.close()

            return

        student_id = student_data["student_id"]

        print("\n================================")
        print("     APPLY FOR PLACEMENT")
        print("================================")

        drive_id = input("Enter Drive ID: ")

        if not drive_id.isdigit():
            print("\nInvalid Drive ID.")

            cursor.close()
            connection.close()

            return

        drive_id = int(drive_id)

        # Check whether the drive exists and is open
        drive_query = """
            SELECT
                d.drive_id,
                d.drive_title,
                c.company_name,
                d.drive_status,
                d.application_deadline
            FROM drive d
            INNER JOIN company c
                ON d.company_id = c.company_id
            WHERE d.drive_id = %s
              AND d.drive_status = 'OPEN'
        """

        cursor.execute(drive_query, (drive_id,))

        drive = cursor.fetchone()

        if drive is None:
            print("\nPlacement drive not found or is not open.")

            cursor.close()
            connection.close()

            return

        # Check for an existing application
        existing_query = """
            SELECT application_id, status
            FROM student_application
            WHERE student_id = %s
              AND drive_id = %s
        """

        cursor.execute(
            existing_query,
            (student_id, drive_id)
        )

        existing_application = cursor.fetchone()

        if existing_application is not None:
            print("\nYou have already applied for this drive.")
            print("Application ID:",
                  existing_application["application_id"])
            print("Status:",
                  existing_application["status"])

            cursor.close()
            connection.close()

            return

        print("\nCompany:", drive["company_name"])
        print("Drive:", drive["drive_title"])
        print("Application Deadline:",
              drive["application_deadline"])

        confirm = input("\nApply for this drive? (Y/N): ")

        if confirm.upper() != "Y":
            print("\nApplication cancelled.")

            cursor.close()
            connection.close()

            return

        insert_query = """
            INSERT INTO student_application (
                student_id,
                drive_id,
                status
            )
            VALUES (
                %s,
                %s,
                'APPLIED'
            )
        """

        cursor.execute(
            insert_query,
            (student_id, drive_id)
        )

        connection.commit()

        print("\nApplication submitted successfully!")
        print("Application ID:",
              cursor.lastrowid)

        cursor.close()
        connection.close()


    def apply_for_leave(self, user):

        connection = create_connection()
        cursor = connection.cursor()

        print("\n================================")
        print("          APPLY FOR LEAVE")
        print("================================")

        from_date = input("Enter From Date (YYYY-MM-DD): ")
        to_date = input("Enter To Date (YYYY-MM-DD): ")

        print("\nLeave Types:")
        print("1. CASUAL")
        print("2. MEDICAL")
        print("3. ACADEMIC")
        print("4. OTHER")

        leave_choice = input("Select Leave Type: ")

        leave_types = {
            "1": "CASUAL",
            "2": "MEDICAL",
            "3": "ACADEMIC",
            "4": "OTHER"
        }

        if leave_choice not in leave_types:
            print("\nInvalid leave type.")

            cursor.close()
            connection.close()

            return

        leave_type = leave_types[leave_choice]

        reason = input("Enter Reason: ").strip()

        if not reason:
            print("\nReason cannot be empty.")

            cursor.close()
            connection.close()

            return

        # Validate dates
        from datetime import datetime

        try:

            start_date = datetime.strptime(
                from_date,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                to_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            print("\nInvalid date format.")
            print("Please use YYYY-MM-DD.")

            cursor.close()
            connection.close()

            return

        if end_date < start_date:

            print("\nTo Date cannot be before From Date.")

            cursor.close()
            connection.close()

            return

        # Calculate number of days in Python
        number_of_days = (
            end_date - start_date
        ).days + 1

        print("\n--------------------------------")
        print("Leave Type:", leave_type)
        print("From Date:", start_date)
        print("To Date:", end_date)
        print("Number of Days:", number_of_days)
        print("Reason:", reason)

        confirm = input("\nSubmit leave request? (Y/N): ")

        if confirm.upper() != "Y":

            print("\nLeave request cancelled.")

            cursor.close()
            connection.close()

            return

        query = """
            INSERT INTO leave_request (
                user_id,
                from_date,
                to_date,
                reason,
                leave_type,
                curr_status
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                'INITIAL_STAGE'
            )
        """

        cursor.execute(
            query,
            (
                user.user_id,
                start_date,
                end_date,
                reason,
                leave_type
            )
        )

        connection.commit()

        request_id = cursor.lastrowid

        print("\nLeave request submitted successfully!")
        print("Request ID:", request_id)
        print("Status: INITIAL_STAGE")

        cursor.close()
        connection.close()