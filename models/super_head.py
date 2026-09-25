class SuperHead:
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
        emergency_contact,
        status
    ):
        self.super_head_id = super_head_id
        self.user_id = user_id
        self.designation = designation
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.blood_group = blood_group
        self.father_name = father_name
        self.mother_name = mother_name
        self.address = address
        self.city = city
        self.state = state
        self.pincode = pincode
        self.qualification = qualification
        self.joining_date = joining_date
        self.salary = salary
        self.emergency_contact = emergency_contact
        self.status = status

    def display_info(self):
        print("Super Head ID:", self.super_head_id)
        print("User ID:", self.user_id)
        print("Designation:", self.designation)
        print("Date of Birth:", self.date_of_birth)
        print("Gender:", self.gender)
        print("Blood Group:", self.blood_group)
        print("Father Name:", self.father_name)
        print("Mother Name:", self.mother_name)
        print("Address:", self.address)
        print("City:", self.city)
        print("State:", self.state)
        print("Pincode:", self.pincode)
        print("Qualification:", self.qualification)
        print("Joining Date:", self.joining_date)
        print("Salary:", self.salary)
        print("Emergency Contact:", self.emergency_contact)
        print("Status:", self.status)