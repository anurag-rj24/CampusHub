class Admin:
    """Represents a system administrator with operational authority across modules."""

    VALID_EMPLOYMENT_TYPES = ("FULL_TIME", "PART_TIME", "CONTRACT")
    VALID_STATUSES = ("ACTIVE", "INACTIVE", "RETIRED")

    def __init__(
        self,
        admin_id,
        user_id,
        department_id,
        designation,
        date_of_birth,
        gender,
        blood_group,
        father_name,
        mother_name,
        address,
        city,
        state,
        pincode,
        qualification,
        joining_date,
        salary,
        employment_type="FULL_TIME",
        emergency_contact=None,
        status="ACTIVE"
    ):
        self.admin_id = admin_id
        self.user_id = user_id
        self.department_id = department_id
        self.designation = designation
        self.date_of_birth = str(date_of_birth)
        self.gender = gender.upper() if gender else "MALE"
        self.blood_group = blood_group
        self.father_name = father_name
        self.mother_name = mother_name
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.qualification = qualification
        self.joining_date = str(joining_date)
        self.salary = float(salary) if salary is not None else 0.0
        self.employment_type = employment_type.upper() if employment_type in self.VALID_EMPLOYMENT_TYPES else "FULL_TIME"
        self.emergency_contact = emergency_contact
        self.status = status.upper() if status in self.VALID_STATUSES else "ACTIVE"

    @property
    def is_active(self):
        return self.status == "ACTIVE"

    def to_dict(self):
        return {
            "admin_id": self.admin_id,
            "user_id": self.user_id,
            "department_id": self.department_id,
            "designation": self.designation,
            "qualification": self.qualification,
            "joining_date": self.joining_date,
            "salary": self.salary,
            "employment_type": self.employment_type,
            "status": self.status
        }

    def display_info(self):
        print("Admin ID:", self.admin_id)
        print("User ID:", self.user_id)
        print("Department ID:", self.department_id)
        print("Designation:", self.designation)
        print("Qualification:", self.qualification)
        print("Joining Date:", self.joining_date)
        print("Employment Type:", self.employment_type)
        print("Salary:", self.salary)
        print("Status:", self.status)