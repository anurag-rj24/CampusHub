class SuperHead:
    """Represents the executive director or principal with governance authority over the campus."""

    VALID_STATUSES = ("ACTIVE", "INACTIVE", "RETIRED")

    def __init__(
        self,
        super_head_id,
        user_id,
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
        emergency_contact=None,
        status="ACTIVE"
    ):
        self.super_head_id = super_head_id
        self.user_id = user_id
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
        self.emergency_contact = emergency_contact
        self.status = status.upper() if status in self.VALID_STATUSES else "ACTIVE"

    @property
    def is_active(self):
        return self.status == "ACTIVE"

    def to_dict(self):
        return {
            "super_head_id": self.super_head_id,
            "user_id": self.user_id,
            "designation": self.designation,
            "qualification": self.qualification,
            "joining_date": self.joining_date,
            "salary": self.salary,
            "status": self.status
        }

    def display_info(self):
        print("Super Head ID:", self.super_head_id)
        print("User ID:", self.user_id)
        print("Designation:", self.designation)
        print("Date of Birth:", self.date_of_birth)
        print("Gender:", self.gender)
        print("Blood Group:", self.blood_group)
        print("Qualification:", self.qualification)
        print("Joining Date:", self.joining_date)
        print("Status:", self.status)