class Course:
    """Represents a degree or diploma program offered by a department."""

    VALID_DEGREE_LEVELS = ("DIPLOMA", "UG", "PG", "PHD")

    def __init__(self, course_id, course_name, course_code, duration_years, department_id, degree_level="UG"):
        self.course_id = course_id
        self.course_name = course_name
        self.course_code = course_code.upper() if course_code else ""
        self.duration_years = int(duration_years) if duration_years is not None else 4
        self.department_id = department_id
        self.degree_level = degree_level.upper() if degree_level in self.VALID_DEGREE_LEVELS else "UG"

    @property
    def total_semesters(self):
        return self.duration_years * 2

    def to_dict(self):
        return {
            "course_id": self.course_id,
            "course_name": self.course_name,
            "course_code": self.course_code,
            "duration_years": self.duration_years,
            "department_id": self.department_id,
            "degree_level": self.degree_level,
            "total_semesters": self.total_semesters
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            course_id=data.get("course_id"),
            course_name=data.get("course_name", ""),
            course_code=data.get("course_code", ""),
            duration_years=data.get("duration_years", 4),
            department_id=data.get("department_id"),
            degree_level=data.get("degree_level", "UG")
        )

    def display_info(self):
        print(f"Course: {self.course_name} ({self.course_code}) | Level: {self.degree_level}")
        print(f"Duration: {self.duration_years} Years ({self.total_semesters} Semesters) | Dept ID: {self.department_id}")

    def __str__(self):
        return f"{self.course_name} [{self.course_code}] - {self.degree_level}"
