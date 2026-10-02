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


class AuditService:
    """Service to record and view system audit logs."""

    @staticmethod
    def log_action(user_id, action, table_name=None, record_id=None, description=None, ip_address="127.0.0.1"):
        """Record an action in the audit_log table."""
        query = """
            INSERT INTO audit_log (user_id, action, table_name, record_id, description, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            with db_cursor(commit=True) as cursor:
                cursor.execute(query, (user_id, action, table_name, record_id, description, ip_address))
        except Exception as e:
            # Audit logging failure should not break main flow
            pass

    def view_all_logs(self, limit=50):
        """View recent system audit logs with user details."""
        query = """
            SELECT a.log_id, a.user_id, u.first_name, u.last_name, u.role,
                   a.action, a.table_name, a.record_id, a.description, a.ip_address, a.created_at
            FROM audit_log a
            LEFT JOIN users u ON a.user_id = u.user_id
            ORDER BY a.log_id DESC
            LIMIT %s
        """
        with db_cursor() as cursor:
            cursor.execute(query, (limit,))
            logs = cursor.fetchall()

        if not logs:
            print("\nNo audit logs found.")
            return

        print("\n================================")
        print(f"     SYSTEM AUDIT LOGS (Last {limit})")
        print("================================")
        for log in logs:
            user_str = f"{log['first_name']} {log['last_name']} ({log['role']})" if log['first_name'] else f"User #{log['user_id']}"
            print(f"\n[Log #{log['log_id']}] {log['created_at']} | Action: {log['action']}")
            print(f"User: {user_str} | IP: {log['ip_address']}")
            if log['table_name']:
                print(f"Target: {log['table_name']} (ID: {log['record_id'] or 'N/A'})")
            if log['description']:
                print(f"Details: {log['description']}")
            print("--------------------------------")

    def view_user_logs(self, user_id):
        """View audit trail for a specific user."""
        query = """
            SELECT log_id, action, table_name, record_id, description, ip_address, created_at
            FROM audit_log
            WHERE user_id = %s
            ORDER BY log_id DESC
            LIMIT 30
        """
        with db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            logs = cursor.fetchall()

        if not logs:
            print(f"\nNo audit logs found for User ID {user_id}.")
            return

        print("\n================================")
        print(f"      USER AUDIT TRAIL (ID: {user_id})")
        print("================================")
        for log in logs:
            print(f"[{log['created_at']}] Action: {log['action']} | Table: {log['table_name'] or 'N/A'}")
            if log['description']:
                print(f"Details: {log['description']}")
            print("--------------------------------")
