class Student:
    """Represents a student enrolled in the institution."""

    VALID_STATUSES = ("ACTIVE", "GRADUATED", "SUSPENDED", "DROPPED")

    def __init__(
        self,
        student_id,
        user_id,
        date_of_birth,
        gender,
        blood_group,
        father_name,
        mother_name,
        previous_qualification,
        previous_percentage,
        admission_date,
        department_id,
        address,
        city=None,
        state=None,
        pincode=None,
        emergency_contact=None,
        student_status="ACTIVE",
        enrollment_number=None
    ):
        self.student_id = student_id
        self.user_id = user_id
        self.date_of_birth = str(date_of_birth)
        self.gender = gender.upper() if gender else "MALE"
        self.blood_group = blood_group
        self.father_name = father_name
        self.mother_name = mother_name
        self.previous_qualification = previous_qualification
        self.previous_percentage = float(previous_percentage) if previous_percentage is not None else None
        self.admission_date = str(admission_date)
        self.department_id = department_id
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.emergency_contact = emergency_contact
        self.student_status = student_status.upper() if student_status in self.VALID_STATUSES else "ACTIVE"
        self.enrollment_number = enrollment_number

    @property
    def is_active(self):
        return self.student_status == "ACTIVE"

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "user_id": self.user_id,
            "enrollment_number": self.enrollment_number,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "father_name": self.father_name,
            "mother_name": self.mother_name,
            "previous_qualification": self.previous_qualification,
            "previous_percentage": self.previous_percentage,
            "admission_date": self.admission_date,
            "department_id": self.department_id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "pincode": self.pincode,
            "emergency_contact": self.emergency_contact,
            "student_status": self.student_status
        }

    def display_info(self):
        print("Student ID:", self.student_id)
        print("User ID:", self.user_id)
        print("Enrollment Number:", self.enrollment_number or "N/A")
        print("Date of Birth:", self.date_of_birth)
        print("Gender:", self.gender)
        print("Blood Group:", self.blood_group)
        print("Father Name:", self.father_name)
        print("Mother Name:", self.mother_name)
        print("Previous Qualification:", self.previous_qualification)
        print("Previous Percentage:", self.previous_percentage)
        print("Admission Date:", self.admission_date)
        print("Department ID:", self.department_id)
        print("Address:", self.address)
        print("City:", self.city)
        print("State:", self.state)
        print("Pincode:", self.pincode)
        print("Emergency Contact:", self.emergency_contact)
        print("Student Status:", self.student_status)