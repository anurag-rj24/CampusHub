class User:
    def __init__(
        self,
        user_id,
        first_name,
        middle_name,
        last_name,
        email,
        phone,
        password_hash,
        role,
        status,
        created_at=None,
        last_login=None
    ):
        self.user_id = user_id
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.created_at = created_at
        self.last_login = last_login

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"

        return f"{self.first_name} {self.last_name}"

    def display_info(self):
        print("User ID:", self.user_id)
        print("Name:", self.get_full_name())
        print("Email:", self.email)
        print("Phone:", self.phone)
        print("Role:", self.role)
        print("Status:", self.status)
        print("Created At:", self.created_at)
        print("Last Login:", self.last_login)