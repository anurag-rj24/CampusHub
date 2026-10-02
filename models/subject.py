class Subject:
    """Represents an academic subject/course module."""

    VALID_TYPES = ("THEORY", "LAB", "TUTORIAL")

    def __init__(self, subject_id, subject_code, subject_name, credits, semester, department_id, subject_type="THEORY"):
        self.subject_id = subject_id
        self.subject_code = subject_code.upper() if subject_code else ""
        self.subject_name = subject_name
        self.credits = int(credits) if credits is not None else 3
        self.semester = int(semester) if semester is not None else 1
        self.department_id = department_id
        self.subject_type = subject_type.upper() if subject_type in self.VALID_TYPES else "THEORY"

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "subject_code": self.subject_code,
            "subject_name": self.subject_name,
            "credits": self.credits,
            "semester": self.semester,
            "subject_type": self.subject_type,
            "department_id": self.department_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            subject_id=data.get("subject_id"),
            subject_code=data.get("subject_code", ""),
            subject_name=data.get("subject_name", ""),
            credits=data.get("credits", 3),
            semester=data.get("semester", 1),
            department_id=data.get("department_id"),
            subject_type=data.get("subject_type", "THEORY")
        )

    def display_info(self):
        print(f"Subject: {self.subject_name} ({self.subject_code})")
        print(f"Credits: {self.credits} | Semester: {self.semester} | Type: {self.subject_type}")

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name} ({self.credits} Credits)"
