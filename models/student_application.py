class StudentApplication:
    """Represents a student's application to a placement drive."""

    VALID_STATUSES = ("APPLIED", "SHORTLISTED", "REJECTED", "SELECTED")

    def __init__(self, application_id, student_id, drive_id, status="APPLIED", remarks=None, applied_at=None, updated_at=None):
        self.application_id = application_id
        self.student_id = student_id
        self.drive_id = drive_id
        self.status = status.upper() if status in self.VALID_STATUSES else "APPLIED"
        self.remarks = remarks
        self.applied_at = applied_at
        self.updated_at = updated_at

    @property
    def is_selected(self):
        return self.status == "SELECTED"

    @property
    def is_shortlisted(self):
        return self.status == "SHORTLISTED"

    def to_dict(self):
        return {
            "application_id": self.application_id,
            "student_id": self.student_id,
            "drive_id": self.drive_id,
            "status": self.status,
            "remarks": self.remarks,
            "applied_at": str(self.applied_at) if self.applied_at else None,
            "updated_at": str(self.updated_at) if self.updated_at else None
        }
