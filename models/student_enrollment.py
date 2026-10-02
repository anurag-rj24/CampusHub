class StudentEnrollment:
    """Represents a student's enrollment in a course for a specific academic semester."""

    VALID_STATUSES = ("ACTIVE", "COMPLETED", "DROPPED")

    def __init__(self, enrollment_id, student_id, course_id, academic_year, semester, enrollment_date, status="ACTIVE", completion_date=None, enrolled_at=None):
        self.enrollment_id = enrollment_id
        self.student_id = student_id
        self.course_id = course_id
        self.academic_year = academic_year
        self.semester = int(semester) if semester is not None else 1
        self.enrollment_date = str(enrollment_date)
        self.status = status.upper() if status in self.VALID_STATUSES else "ACTIVE"
        self.completion_date = str(completion_date) if completion_date else None
        self.enrolled_at = enrolled_at

    @property
    def is_active(self):
        return self.status == "ACTIVE"

    def to_dict(self):
        return {
            "enrollment_id": self.enrollment_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "academic_year": self.academic_year,
            "semester": self.semester,
            "enrollment_date": self.enrollment_date,
            "status": self.status,
            "completion_date": self.completion_date
        }
