from database.connection import create_connection


class FacultyService:

    def show_dashboard(self, user):
        while True:
            print("\n================================")
            print("       FACULTY DASHBOARD")
            print("================================")
            print("Welcome,", user.get_full_name())
            print()
            print("1. View Profile")
            print("2. Manage Attendance")
            print("3. Manage Marks")
            print("4. View Subjects")
            print("5. View Notices")
            print("6. View Leave Requests")
            print("7. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                user.display_info()

            elif choice == "2":
               self.manage_attendance(user)

            elif choice == "3":
                self.manage_marks(user)

            elif choice == "4":
                 self.view_subjects(user)

            elif choice == "5":
                self.view_notices(user)

            elif choice == "6":
                self.manage_leave_requests(user)

            elif choice == "7":
                print("\nLogging out...")
                break

            else:
                print("\nInvalid choice. Please try again.")


    def view_subjects(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                s.subject_id,
                s.subject_code,
                s.subject_name,
                s.credits,
                s.semester,
                s.subject_type,
                d.department_name,
                fs.assigned_at

            FROM faculty_subject fs

            INNER JOIN faculty f
                ON fs.faculty_id = f.faculty_id

            INNER JOIN subject s
                ON fs.subject_id = s.subject_id

            INNER JOIN department d
                ON s.department_id = d.department_id

            WHERE f.user_id = %s

            ORDER BY s.semester, s.subject_code
        """

        cursor.execute(query, (user.user_id,))

        subjects = cursor.fetchall()

        if not subjects:

            print("\nNo subjects assigned.")

            cursor.close()
            connection.close()

            return

        print("\n================================")
        print("        ASSIGNED SUBJECTS")
        print("================================")

        for subject in subjects:

            print("\n--------------------------------")
            print("Subject ID:", subject["subject_id"])
            print("Subject Code:", subject["subject_code"])
            print("Subject Name:", subject["subject_name"])
            print("Credits:", subject["credits"])
            print("Semester:", subject["semester"])
            print("Subject Type:", subject["subject_type"])
            print("Department:", subject["department_name"])
            print("Assigned At:", subject["assigned_at"])

        cursor.close()
        connection.close()

    def manage_attendance(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Find faculty_id
        faculty_query = """
            SELECT faculty_id
            FROM faculty
            WHERE user_id = %s
        """

        cursor.execute(faculty_query, (user.user_id,))
        faculty_data = cursor.fetchone()

        if faculty_data is None:
            print("\nFaculty profile not found.")
            cursor.close()
            connection.close()
            return

        faculty_id = faculty_data["faculty_id"]

        # Find class sessions handled by this faculty
        session_query = """
            SELECT
                cs.session_id,
                cs.session_date,
                cs.start_time,
                cs.end_time,
                cs.room_no,
                cs.session_type,
                s.subject_code,
                s.subject_name
            FROM class_session cs

            INNER JOIN subject s
                ON cs.subject_id = s.subject_id

            WHERE cs.faculty_id = %s

            ORDER BY cs.session_date DESC, cs.start_time DESC
        """

        cursor.execute(session_query, (faculty_id,))
        sessions = cursor.fetchall()

        if not sessions:
            print("\nNo class sessions found.")
            cursor.close()
            connection.close()
            return

        print("\n================================")
        print("       MANAGE ATTENDANCE")
        print("================================")

        for session in sessions:
            print("\n--------------------------------")
            print("Session ID:", session["session_id"])
            print("Subject:", session["subject_code"],
                  "-", session["subject_name"])
            print("Date:", session["session_date"])
            print("Time:", session["start_time"],
                  "-", session["end_time"])
            print("Room:", session["room_no"])
            print("Type:", session["session_type"])

        session_id = input("\nEnter Session ID: ")

        if not session_id.isdigit():
            print("\nInvalid Session ID.")
            cursor.close()
            connection.close()
            return

        session_id = int(session_id)

        # Verify that the selected session belongs to this faculty
        valid_session_query = """
            SELECT session_id
            FROM class_session
            WHERE session_id = %s
              AND faculty_id = %s
        """

        cursor.execute(
            valid_session_query,
            (session_id, faculty_id)
        )

        valid_session = cursor.fetchone()

        if valid_session is None:
            print("\nInvalid session.")
            cursor.close()
            connection.close()
            return

        # Get students
        student_query = """
            SELECT
                student_id,
                user_id
            FROM student
            WHERE student_status = 'ACTIVE'
            ORDER BY student_id
        """

        cursor.execute(student_query)
        students = cursor.fetchall()

        if not students:
            print("\nNo active students found.")
            cursor.close()
            connection.close()
            return

        print("\n================================")
        print("          STUDENT LIST")
        print("================================")

        for student in students:

            print("\nStudent ID:", student["student_id"])

            status = input(
                "Attendance (P = Present, A = Absent): "
            ).strip().upper()

            if status == "P":
                attendance_status = "PRESENT"
            elif status == "A":
                attendance_status = "ABSENT"
            else:
                print("Invalid input. Student skipped.")
                continue

            remarks = input("Remarks (optional): ").strip()

            # Check whether attendance already exists
            check_query = """
                SELECT attendance_id
                FROM attendance
                WHERE student_id = %s
                  AND session_id = %s
            """

            cursor.execute(
                check_query,
                (student["student_id"], session_id)
            )

            existing = cursor.fetchone()

            if existing:

                update_query = """
                    UPDATE attendance
                    SET
                        status = %s,
                        remarks = %s,
                        marked_at = CURRENT_TIMESTAMP
                    WHERE attendance_id = %s
                """

                cursor.execute(
                    update_query,
                    (
                        attendance_status,
                        remarks if remarks else None,
                        existing["attendance_id"]
                    )
                )

            else:

                insert_query = """
                    INSERT INTO attendance (
                        student_id,
                        session_id,
                        status,
                        remarks
                    )
                    VALUES (%s, %s, %s, %s)
                """

                cursor.execute(
                    insert_query,
                    (
                        student["student_id"],
                        session_id,
                        attendance_status,
                        remarks if remarks else None
                    )
                )

        connection.commit()

        print("\nAttendance saved successfully.")

        cursor.close()
        connection.close()


    def manage_marks(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        # Find faculty_id
        faculty_query = """
            SELECT faculty_id
            FROM faculty
            WHERE user_id = %s
        """

        cursor.execute(faculty_query, (user.user_id,))
        faculty_data = cursor.fetchone()

        if faculty_data is None:
            print("\nFaculty profile not found.")
            cursor.close()
            connection.close()
            return

        faculty_id = faculty_data["faculty_id"]

        # Show subjects assigned to this faculty
        subject_query = """
            SELECT
                s.subject_id,
                s.subject_code,
                s.subject_name,
                s.semester
            FROM faculty_subject fs

            INNER JOIN subject s
                ON fs.subject_id = s.subject_id

            WHERE fs.faculty_id = %s

            ORDER BY s.semester, s.subject_code
        """

        cursor.execute(subject_query, (faculty_id,))
        subjects = cursor.fetchall()

        if not subjects:
            print("\nNo subjects assigned.")
            cursor.close()
            connection.close()
            return

        print("\n================================")
        print("          MANAGE MARKS")
        print("================================")

        for subject in subjects:
            print("\n--------------------------------")
            print("Subject ID:", subject["subject_id"])
            print("Subject Code:", subject["subject_code"])
            print("Subject Name:", subject["subject_name"])
            print("Semester:", subject["semester"])

        subject_id = input("\nEnter Subject ID: ")

        if not subject_id.isdigit():
            print("\nInvalid Subject ID.")
            cursor.close()
            connection.close()
            return

        subject_id = int(subject_id)

        # Verify subject is assigned to this faculty
        valid_subject_query = """
            SELECT subject_id
            FROM faculty_subject
            WHERE faculty_id = %s
              AND subject_id = %s
        """

        cursor.execute(
            valid_subject_query,
            (faculty_id, subject_id)
        )

        valid_subject = cursor.fetchone()

        if valid_subject is None:
            print("\nThis subject is not assigned to you.")
            cursor.close()
            connection.close()
            return

        # Show active students
        student_query = """
            SELECT
                student_id,
                user_id
            FROM student
            WHERE student_status = 'ACTIVE'
            ORDER BY student_id
        """

        cursor.execute(student_query)
        students = cursor.fetchall()

        if not students:
            print("\nNo active students found.")
            cursor.close()
            connection.close()
            return

        academic_year = input("Enter Academic Year (e.g. 2026-27): ")

        semester_input = input("Enter Semester: ")

        if not semester_input.isdigit():
            print("\nInvalid semester.")
            cursor.close()
            connection.close()
            return

        semester = int(semester_input)

        for student in students:

            print("\n--------------------------------")
            print("Student ID:", student["student_id"])

            try:
                cca1 = int(input("CCA 1: "))
                cca2 = int(input("CCA 2: "))
                cca3 = int(input("CCA 3: "))
                midterm = int(input("Midterm: "))
                final_exam = int(input("Final Exam: "))
            except ValueError:
                print("Invalid marks. Student skipped.")
                continue

            if (
                cca1 < 0
                or cca2 < 0
                or cca3 < 0
                or midterm < 0
                or final_exam < 0
            ):
                print("Marks cannot be negative.")
                continue

            total_marks = (
                cca1
                + cca2
                + cca3
                + midterm
                + final_exam
            )

            # Check whether marks already exist
            check_query = """
                SELECT marks_id
                FROM marks
                WHERE student_id = %s
                  AND subject_id = %s
                  AND academic_year = %s
                  AND semester = %s
            """

            cursor.execute(
                check_query,
                (
                    student["student_id"],
                    subject_id,
                    academic_year,
                    semester
                )
            )

            existing = cursor.fetchone()

            if existing:

                update_query = """
                    UPDATE marks
                    SET
                        faculty_id = %s,
                        cca1 = %s,
                        cca2 = %s,
                        cca3 = %s,
                        midterm = %s,
                        final_exam = %s,
                        total_marks = %s
                    WHERE marks_id = %s
                """

                cursor.execute(
                    update_query,
                    (
                        faculty_id,
                        cca1,
                        cca2,
                        cca3,
                        midterm,
                        final_exam,
                        total_marks,
                        existing["marks_id"]
                    )
                )

            else:

                insert_query = """
                    INSERT INTO marks (
                        student_id,
                        subject_id,
                        faculty_id,
                        cca1,
                        cca2,
                        cca3,
                        midterm,
                        final_exam,
                        total_marks,
                        academic_year,
                        semester
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s
                    )
                """

                cursor.execute(
                    insert_query,
                    (
                        student["student_id"],
                        subject_id,
                        faculty_id,
                        cca1,
                        cca2,
                        cca3,
                        midterm,
                        final_exam,
                        total_marks,
                        academic_year,
                        semester
                    )
                )

            print("Total Marks:", total_marks)

        connection.commit()

        print("\nMarks saved successfully.")

        cursor.close()
        connection.close()


    def manage_leave_requests(self, user):

        connection = create_connection()
        cursor = connection.cursor(dictionary=True)

        print("\n================================")
        print("       LEAVE REQUESTS")
        print("================================")

        query = """
            SELECT
                lr.request_id,
                lr.user_id,
                lr.from_date,
                lr.to_date,
                lr.reason,
                lr.leave_type,
                lr.curr_status,
                lr.reviewer_comment,
                lr.applied_at,
                u.first_name,
                u.middle_name,
                u.last_name,
                u.email

            FROM leave_request lr

            INNER JOIN users u
                ON lr.user_id = u.user_id

            ORDER BY lr.applied_at DESC
        """

        cursor.execute(query)

        requests = cursor.fetchall()

        if not requests:
            print("\nNo leave requests found.")

            cursor.close()
            connection.close()

            return

        for request in requests:

            print("\n--------------------------------")
            print("Request ID:", request["request_id"])

            print(
                "Student:",
                request["first_name"],
                request["middle_name"] or "",
                request["last_name"]
            )

            print("Email:", request["email"])
            print("From Date:", request["from_date"])
            print("To Date:", request["to_date"])
            print("Leave Type:", request["leave_type"])
            print("Reason:", request["reason"])
            print("Status:", request["curr_status"])
            print("Applied At:", request["applied_at"])

            print(
                "Reviewer Comment:",
                request["reviewer_comment"]
            )

        request_id = input(
            "\nEnter Request ID to process (0 to go back): "
        )

        if not request_id.isdigit():

            print("\nInvalid Request ID.")

            cursor.close()
            connection.close()

            return

        request_id = int(request_id)

        if request_id == 0:

            cursor.close()
            connection.close()

            return

        # Check selected request
        check_query = """
            SELECT
                request_id,
                curr_status
            FROM leave_request
            WHERE request_id = %s
        """

        cursor.execute(check_query, (request_id,))

        leave_request = cursor.fetchone()

        if leave_request is None:

            print("\nLeave request not found.")

            cursor.close()
            connection.close()

            return

        if leave_request["curr_status"] in (
            "APPROVED",
            "REJECTED"
        ):

            print(
                "\nThis request has already been finalized."
            )

            cursor.close()
            connection.close()

            return

        print("\nSelect Action:")
        print("1. PROCESSING")
        print("2. APPROVED")
        print("3. REJECTED")

        action = input("Enter choice: ")

        status_map = {
            "1": "PROCESSING",
            "2": "APPROVED",
            "3": "REJECTED"
        }

        if action not in status_map:

            print("\nInvalid action.")

            cursor.close()
            connection.close()

            return

        new_status = status_map[action]

        reviewer_comment = input(
            "Enter reviewer comment (optional): "
        ).strip()

        update_query = """
            UPDATE leave_request
            SET
                curr_status = %s,
                reviewed_by = %s,
                reviewer_comment = %s,
                reviewed_at = CURRENT_TIMESTAMP
            WHERE request_id = %s
        """

        # user.user_id is the faculty's user ID
        cursor.execute(
            update_query,
            (
                new_status,
                user.user_id,
                reviewer_comment if reviewer_comment else None,
                request_id
            )
        )

        connection.commit()

        print("\nLeave request updated successfully.")
        print("Request ID:", request_id)
        print("New Status:", new_status)

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
              AND target_role IN ('FACULTY', 'ALL')
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
        print("          FACULTY NOTICES")
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
