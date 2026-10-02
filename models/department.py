class Department:
    """Represents an academic department within the institution."""

    def __init__(self, department_id, department_name, department_code):
        self.department_id = department_id
        self.department_name = department_name
        self.department_code = department_code.upper() if department_code else ""

    def to_dict(self):
        return {
            "department_id": self.department_id,
            "department_name": self.department_name,
            "department_code": self.department_code
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            department_id=data.get("department_id"),
            department_name=data.get("department_name", ""),
            department_code=data.get("department_code", "")
        )

    def display_info(self):
        print(f"[{self.department_code}] {self.department_name} (ID: {self.department_id})")

    def __str__(self):
        return f"{self.department_name} ({self.department_code})"
