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


class LeaveService:
    """Service to handle leave application, tracking, and approval workflow."""

    def apply_leave(self, user):
        print("\n================================")
        print("        APPLY FOR LEAVE")
        print("================================")

        from_date = input("From Date (YYYY-MM-DD): ").strip()
        to_date = input("To Date (YYYY-MM-DD): ").strip()

        print("\nLeave Types:")
        print("1. CASUAL")
        print("2. MEDICAL")
        print("3. ACADEMIC")
        print("4. OTHER")
        type_choice = input("Select Leave Type (1-4): ").strip()
        type_map = {"1": "CASUAL", "2": "MEDICAL", "3": "ACADEMIC", "4": "OTHER"}
        leave_type = type_map.get(type_choice, "CASUAL")

        reason = input("Reason for Leave: ").strip()

        if not from_date or not to_date or not reason:
            print("\nFrom Date, To Date, and Reason are required.")
            return

        query = """
            INSERT INTO leave_request (user_id, from_date, to_date, reason, leave_type, curr_status)
            VALUES (%s, %s, %s, %s, %s, 'INITIAL_STAGE')
        """
        with db_cursor(commit=True) as cursor:
            cursor.execute(query, (user.user_id, from_date, to_date, reason, leave_type))
            print("\n================================")
            print("Leave application submitted successfully!")
            print("Request ID:", cursor.lastrowid)
            print("Status: INITIAL_STAGE (Pending Review)")
            print("================================")

    def view_my_leaves(self, user):
        print("\n================================")
        print("       MY LEAVE APPLICATIONS")
        print("================================")

        query = """
            SELECT lr.request_id, lr.from_date, lr.to_date, lr.leave_type, lr.reason,
                   lr.curr_status, lr.reviewer_comment, lr.applied_at, lr.reviewed_at,
                   u.first_name AS rev_first, u.last_name AS rev_last
            FROM leave_request lr
            LEFT JOIN users u ON lr.reviewed_by = u.user_id
            WHERE lr.user_id = %s
            ORDER BY lr.request_id DESC
        """
        with db_cursor() as cursor:
            cursor.execute(query, (user.user_id,))
            requests = cursor.fetchall()

        if not requests:
            print("\nNo leave applications found.")
            return

        for req in requests:
            print("\n--------------------------------")
            print(f"Request ID: {req['request_id']} | Type: {req['leave_type']}")
            print(f"Duration: {req['from_date']} to {req['to_date']}")
            print(f"Reason: {req['reason']}")
            print(f"Status: {req['curr_status']}")
            print(f"Applied At: {req['applied_at']}")
            if req['reviewed_at']:
                reviewer = f"{req['rev_first']} {req['rev_last']}" if req['rev_first'] else "Admin"
                print(f"Reviewed By: {reviewer} at {req['reviewed_at']}")
                print(f"Reviewer Comment: {req['reviewer_comment'] or 'None'}")

    def view_all_leaves(self, filter_status=None):
        print("\n================================")
        print("     ALL LEAVE APPLICATIONS")
        print("================================")

        query = """
            SELECT lr.request_id, lr.user_id, lr.from_date, lr.to_date, lr.leave_type,
                   lr.reason, lr.curr_status, lr.reviewer_comment, lr.applied_at,
                   u.first_name, u.last_name, u.role, u.email
            FROM leave_request lr
            JOIN users u ON lr.user_id = u.user_id
        """
        params = []
        if filter_status:
            query += " WHERE lr.curr_status = %s"
            params.append(filter_status)
        query += " ORDER BY lr.request_id DESC"

        with db_cursor() as cursor:
            cursor.execute(query, tuple(params))
            requests = cursor.fetchall()

        if not requests:
            print("\nNo leave requests found.")
            return

        for req in requests:
            print("\n--------------------------------")
            print(f"Request ID: {req['request_id']} | Applicant: {req['first_name']} {req['last_name']} ({req['role']})")
            print(f"Email: {req['email']} | User ID: {req['user_id']}")
            print(f"Duration: {req['from_date']} to {req['to_date']} | Type: {req['leave_type']}")
            print(f"Reason: {req['reason']}")
            print(f"Status: {req['curr_status']} | Applied At: {req['applied_at']}")
            if req['reviewer_comment']:
                print(f"Comment: {req['reviewer_comment']}")

    def review_leave(self, reviewer_user):
        print("\n================================")
        print("      REVIEW LEAVE REQUEST")
        print("================================")

        request_id = input("Enter Request ID: ").strip()
        if not request_id.isdigit():
            print("\nInvalid Request ID.")
            return

        with db_cursor(commit=True) as cursor:
            cursor.execute("SELECT * FROM leave_request WHERE request_id = %s", (int(request_id),))
            req = cursor.fetchone()

            if not req:
                print("\nLeave request not found.")
                return

            print(f"\nCurrent Status: {req['curr_status']}")
            print(f"Duration: {req['from_date']} to {req['to_date']}")
            print(f"Reason: {req['reason']}")

            print("\nDecision:")
            print("1. APPROVE")
            print("2. REJECT")
            print("3. PROCESSING")
            choice = input("Enter Choice (1-3): ").strip()
            decision_map = {"1": "APPROVED", "2": "REJECTED", "3": "PROCESSING"}
            new_status = decision_map.get(choice)

            if not new_status:
                print("\nInvalid choice.")
                return

            comment = input("Reviewer Comment: ").strip()
            if new_status == "REJECTED" and not comment:
                print("\nComment is required when rejecting a leave request.")
                return

            update_query = """
                UPDATE leave_request
                SET curr_status = %s, reviewed_by = %s, reviewer_comment = %s,
                    reviewed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                WHERE request_id = %s
            """
            cursor.execute(update_query, (new_status, reviewer_user.user_id, comment or None, int(request_id)))
            print(f"\nLeave request {new_status.lower()} successfully.")
