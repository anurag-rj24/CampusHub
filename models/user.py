class User:
    """Core user model representing any authenticated user in the ERP portal."""

    VALID_ROLES = ("STUDENT", "FACULTY", "ADMIN", "SUPER_HEAD")
    VALID_STATUSES = ("ACTIVE", "INACTIVE")

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
        status="ACTIVE",
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
        self.role = role.upper() if role else "STUDENT"
        self.status = status.upper() if status else "ACTIVE"
        self.created_at = created_at
        self.last_login = last_login

    @property
    def is_active(self):
        return self.status == "ACTIVE"

    def get_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.get_full_name(),
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "status": self.status,
            "created_at": str(self.created_at) if self.created_at else None,
            "last_login": str(self.last_login) if self.last_login else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_id=data.get("user_id"),
            first_name=data.get("first_name", ""),
            middle_name=data.get("middle_name"),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            role=data.get("role", "STUDENT"),
            status=data.get("status", "ACTIVE"),
            created_at=data.get("created_at"),
            last_login=data.get("last_login")
        )

    def display_info(self):
        print("User ID:", self.user_id)
        print("Name:", self.get_full_name())
        print("Email:", self.email)
        print("Phone:", self.phone)
        print("Role:", self.role)
        print("Status:", self.status)
        print("Created At:", self.created_at)
        print("Last Login:", self.last_login)

    def __str__(self):
        return f"{self.get_full_name()} ({self.role}) [{self.email}]"