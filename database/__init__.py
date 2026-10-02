from database.connection import create_connection


def check_db_health():
    """Diagnostic helper to test database connectivity and ping status."""
    try:
        connection = create_connection()
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE(), VERSION()")
            db_name, version = cursor.fetchone()
            cursor.close()
            connection.close()
            return True, f"Connected to {db_name} (MySQL {version})"
        return False, "Unable to establish active database connection."
    except Exception as error:
        return False, f"Database Connection Error: {error}"


__all__ = [
    "create_connection",
    "check_db_health"
]
