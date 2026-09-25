class Student:
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
        city,
        state,
        pincode,
        emergency_contact,
        student_status
    ):
        self.student_id = student_id
        self.user_id = user_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.blood_group = blood_group
        self.father_name = father_name
        self.mother_name = mother_name
        self.previous_qualification = previous_qualification
        self.previous_percentage = previous_percentage
        self.admission_date = admission_date
        self.department_id = department_id
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.emergency_contact = emergency_contact
        self.student_status = student_status

    def display_info(self):
        print("Student ID:", self.student_id)
        print("User ID:", self.user_id)
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