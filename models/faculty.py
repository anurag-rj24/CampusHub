class Faculty:
    def __init__(
        self,
        faculty_id,
        user_id,
        department_id,
        date_of_birth,
        gender,
        blood_group,
        father_name,
        mother_name,
        address,
        city,
        state,
        pincode,
        designation,
        qualification,
        specialization,
        joining_date,
        salary,
        employment_type,
        emergency_contact,
        status
    ):
        self.faculty_id = faculty_id
        self.user_id = user_id
        self.department_id = department_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.blood_group = blood_group
        self.father_name = father_name
        self.mother_name = mother_name
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.designation = designation
        self.qualification = qualification
        self.specialization = specialization
        self.joining_date = joining_date
        self.salary = salary
        self.employment_type = employment_type
        self.emergency_contact = emergency_contact
        self.status = status

    def display_info(self):
        print("Faculty ID:", self.faculty_id)
        print("User ID:", self.user_id)
        print("Department ID:", self.department_id)
        print("Date of Birth:", self.date_of_birth)
        print("Gender:", self.gender)
        print("Blood Group:", self.blood_group)
        print("Father Name:", self.father_name)
        print("Mother Name:", self.mother_name)
        print("Address:", self.address)
        print("City:", self.city)
        print("State:", self.state)
        print("Pincode:", self.pincode)
        print("Designation:", self.designation)
        print("Qualification:", self.qualification)
        print("Specialization:", self.specialization)
        print("Joining Date:", self.joining_date)
        print("Salary:", self.salary)
        print("Employment Type:", self.employment_type)
        print("Emergency Contact:", self.emergency_contact)
        print("Status:", self.status)