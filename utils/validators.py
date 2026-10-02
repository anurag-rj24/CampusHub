import re
from datetime import datetime


class Validators:
    """Comprehensive input validation utilities for the CampusHub ERP portal."""

    BLOOD_GROUPS = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-")
    GENDERS = ("MALE", "FEMALE", "OTHER")
    ROLES = ("STUDENT", "FACULTY", "ADMIN", "SUPER_HEAD")
    EMPLOYMENT_TYPES = ("FULL_TIME", "PART_TIME", "CONTRACT")
    DEGREE_LEVELS = ("DIPLOMA", "UG", "PG", "PHD")
    SUBJECT_TYPES = ("THEORY", "LAB", "TUTORIAL")
    LEAVE_TYPES = ("CASUAL", "MEDICAL", "ACADEMIC", "OTHER")
    DRIVE_STATUSES = ("UPCOMING", "OPEN", "CLOSED", "CANCELLED")

    @staticmethod
    def is_valid_email(email):
        """Validates standard email format."""
        if not email or not isinstance(email, str):
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def is_valid_phone(phone):
        """Validates phone number (10 digits or with optional country code)."""
        if not phone or not isinstance(phone, str):
            return False
        clean = re.sub(r"[\s\-\(\)\+]", "", phone.strip())
        return clean.isdigit() and len(clean) in (10, 11, 12, 13)

    @staticmethod
    def is_valid_date(date_str, fmt="%Y-%m-%d"):
        """Validates if date string conforms to specified format and is a real calendar date."""
        if not date_str or not isinstance(date_str, str):
            return False
        try:
            datetime.strptime(date_str.strip(), fmt)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_blood_group(blood_group):
        """Validates standard blood group classifications."""
        if not blood_group:
            return True  # Optional field
        return blood_group.strip().upper() in Validators.BLOOD_GROUPS

    @staticmethod
    def is_valid_gender(gender):
        """Validates gender category."""
        if not gender:
            return False
        return gender.strip().upper() in Validators.GENDERS

    @staticmethod
    def is_valid_pincode(pincode):
        """Validates 6-digit postal code."""
        if not pincode:
            return True  # Optional
        clean = pincode.strip()
        return clean.isdigit() and len(clean) in (5, 6)

    @staticmethod
    def is_valid_percentage(val):
        """Validates percentage between 0.0 and 100.0."""
        if val is None or val == "":
            return True
        try:
            num = float(val)
            return 0.0 <= num <= 100.0
        except ValueError:
            return False

    @staticmethod
    def is_valid_cgpa(val):
        """Validates CGPA scale between 0.0 and 10.0."""
        if val is None or val == "":
            return True
        try:
            num = float(val)
            return 0.0 <= num <= 10.0
        except ValueError:
            return False

    @staticmethod
    def validate_password_strength(password):
        """
        Validates password strength:
        - Minimum 6 characters
        - Must contain at least one digit or special character
        """
        if not password or len(password) < 6:
            return False, "Password must be at least 6 characters long."
        if not any(char.isdigit() for char in password) and not any(not char.isalnum() for char in password):
            return False, "Password must contain at least one digit or special symbol."
        return True, "Strong password"
