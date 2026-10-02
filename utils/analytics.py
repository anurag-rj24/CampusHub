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


class ERPAnalytics:
    """Advanced Business Intelligence & Analytics engine for the CampusHub ERP portal."""

    @staticmethod
    def get_academic_performance_summary():
        """Computes campus-wide grade distributions and student performance tiers."""
        query = """
            SELECT
                COUNT(m.marks_id) AS total_assessments,
                AVG(m.total_marks) AS avg_score,
                MAX(m.total_marks) AS highest_score,
                MIN(m.total_marks) AS lowest_score,
                SUM(CASE WHEN m.total_marks >= 80 THEN 1 ELSE 0 END) AS distinction_count,
                SUM(CASE WHEN m.total_marks >= 50 AND m.total_marks < 80 THEN 1 ELSE 0 END) AS passing_count,
                SUM(CASE WHEN m.total_marks < 40 THEN 1 ELSE 0 END) AS at_risk_count
            FROM marks m
        """
        with db_cursor() as cursor:
            cursor.execute(query)
            stats = cursor.fetchone()

        return stats or {}

    @staticmethod
    def get_attendance_risk_alerts(threshold=75.0):
        """Identifies students currently at risk due to low attendance across all subjects."""
        query = """
            SELECT s.student_id, u.first_name, u.last_name, u.email, d.department_name,
                   COUNT(a.attendance_id) AS total_classes,
                   SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) AS attended_classes
            FROM student s
            JOIN users u ON s.user_id = u.user_id
            JOIN department d ON s.department_id = d.department_id
            JOIN attendance a ON s.student_id = a.student_id
            WHERE s.student_status = 'ACTIVE'
            GROUP BY s.student_id, u.first_name, u.last_name, u.email, d.department_name
            HAVING (SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) / COUNT(a.attendance_id) * 100) < %s
            ORDER BY (SUM(CASE WHEN a.status = 'PRESENT' THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) ASC
        """
        with db_cursor() as cursor:
            cursor.execute(query, (threshold,))
            risk_list = cursor.fetchall()

        return risk_list or []

    @staticmethod
    def get_placement_conversion_metrics():
        """Calculates placement drive participation, offers made, and average package."""
        query = """
            SELECT
                COUNT(DISTINCT d.drive_id) AS total_drives,
                COUNT(DISTINCT sa.application_id) AS total_applications,
                SUM(CASE WHEN sa.status = 'SELECTED' THEN 1 ELSE 0 END) AS total_placed_offers,
                AVG(d.package_in_lpa) AS avg_package_lpa,
                MAX(d.package_in_lpa) AS max_package_lpa
            FROM drive d
            LEFT JOIN student_application sa ON d.drive_id = sa.drive_id
        """
        with db_cursor() as cursor:
            cursor.execute(query)
            metrics = cursor.fetchone()

        return metrics or {}
