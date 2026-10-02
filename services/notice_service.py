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


class NoticeService:
    """Service to handle campus notice board publications, role filtering, and notice management."""

    def view_notices_for_user(self, user):
        print("\n================================")
        print("         CAMPUS NOTICES")
        print("================================")

        query = """
            SELECT n.notice_id, n.title, n.content, n.release_date, n.valid_till, n.target_role,
                   u.first_name, u.last_name, u.role AS author_role
            FROM notice n
            LEFT JOIN users u ON n.created_by = u.user_id
            WHERE n.is_active = 1
              AND (n.target_role = 'ALL' OR n.target_role = %s)
              AND (n.valid_till IS NULL OR n.valid_till >= CURRENT_DATE)
            ORDER BY n.release_date DESC, n.notice_id DESC
        """
        with db_cursor() as cursor:
            cursor.execute(query, (user.role,))
            notices = cursor.fetchall()

        if not notices:
            print("\nNo active notices available at this time.")
            return

        for notice in notices:
            author = f"{notice['first_name']} {notice['last_name']} ({notice['author_role']})" if notice['first_name'] else "Administration"
            print("\n==================================================")
            print(f"[{notice['notice_id']}] {notice['title']}")
            print(f"Target: {notice['target_role']} | Date: {notice['release_date']} | Valid Till: {notice['valid_till'] or 'Ongoing'}")
            print(f"Published by: {author}")
            print("--------------------------------------------------")
            print(notice['content'])
            print("==================================================")

    def view_all_notices(self):
        print("\n================================")
        print("       ALL SYSTEM NOTICES")
        print("================================")

        query = """
            SELECT n.notice_id, n.title, n.release_date, n.valid_till, n.target_role, n.is_active,
                   u.first_name, u.last_name
            FROM notice n
            LEFT JOIN users u ON n.created_by = u.user_id
            ORDER BY n.notice_id DESC
        """
        with db_cursor() as cursor:
            cursor.execute(query)
            notices = cursor.fetchall()

        if not notices:
            print("\nNo notices found.")
            return

        for n in notices:
            status = "ACTIVE" if n['is_active'] else "INACTIVE"
            author = f"{n['first_name']} {n['last_name']}" if n['first_name'] else "Admin"
            print("\n--------------------------------")
            print(f"Notice ID: {n['notice_id']} | Status: {status} | Target: {n['target_role']}")
            print(f"Title: {n['title']}")
            print(f"Date: {n['release_date']} | Valid Till: {n['valid_till'] or 'N/A'} | By: {author}")

    def publish_notice(self, user):
        print("\n================================")
        print("        PUBLISH NEW NOTICE")
        print("================================")

        title = input("Notice Title: ").strip()
        content = input("Notice Content: ").strip()
        release_date = input("Release Date (YYYY-MM-DD): ").strip()
        valid_till = input("Valid Till (YYYY-MM-DD, optional): ").strip() or None

        print("\nTarget Roles:")
        print("1. ALL")
        print("2. STUDENT")
        print("3. FACULTY")
        print("4. ADMIN")
        choice = input("Select Target Role (1-4): ").strip()
        role_map = {"1": "ALL", "2": "STUDENT", "3": "FACULTY", "4": "ADMIN"}
        target_role = role_map.get(choice, "ALL")

        if not title or not content or not release_date:
            print("\nTitle, Content, and Release Date are required.")
            return

        query = """
            INSERT INTO notice (title, content, release_date, valid_till, target_role, created_by, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """
        with db_cursor(commit=True) as cursor:
            cursor.execute(query, (title, content, release_date, valid_till, target_role, user.user_id))
            print("\nNotice published successfully!")
            print("Notice ID:", cursor.lastrowid)
