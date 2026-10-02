class ClassSession:
    """Represents a scheduled lecture, lab, or tutorial class session."""

    def __init__(self, session_id, subject_id, faculty_id, session_date, start_time, end_time, room_no="101", session_type="LECTURE"):
        self.session_id = session_id
        self.subject_id = subject_id
        self.faculty_id = faculty_id
        self.session_date = session_date
        self.start_time = str(start_time)
        self.end_time = str(end_time)
        self.room_no = room_no
        self.session_type = session_type

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "subject_id": self.subject_id,
            "faculty_id": self.faculty_id,
            "session_date": str(self.session_date),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "room_no": self.room_no,
            "session_type": self.session_type
        }


class Attendance:
    """Represents a student's attendance record for a specific class session."""

    def __init__(self, attendance_id, student_id, session_id, status, remarks=None, marked_at=None):
        self.attendance_id = attendance_id
        self.student_id = student_id
        self.session_id = session_id
        self.status = status.upper() if status else "ABSENT"
        self.remarks = remarks
        self.marked_at = marked_at

    @property
    def is_present(self):
        return self.status == "PRESENT"

    def to_dict(self):
        return {
            "attendance_id": self.attendance_id,
            "student_id": self.student_id,
            "session_id": self.session_id,
            "status": self.status,
            "remarks": self.remarks,
            "marked_at": str(self.marked_at) if self.marked_at else None
        }

    @staticmethod
    def calculate_percentage(present_count, total_count):
        if total_count <= 0:
            return 0.0
        return round((present_count / total_count) * 100.0, 2)

    @staticmethod
    def is_eligible_for_exams(percentage, min_required=75.0):
        return percentage >= min_required
