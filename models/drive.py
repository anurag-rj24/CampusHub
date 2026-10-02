class Drive:
    """Represents an on-campus or virtual campus placement drive."""

    VALID_STATUSES = ("UPCOMING", "OPEN", "CLOSED", "CANCELLED")

    def __init__(
        self,
        drive_id,
        company_id,
        drive_title,
        drive_date,
        job_role,
        job_location,
        package_in_lpa,
        role_description=None,
        minimum_cgpa=None,
        minimum_10th_percentage=None,
        minimum_12th_percentage=None,
        maximum_backlogs=0,
        eligible_degree=None,
        eligible_branch=None,
        application_deadline=None,
        created_by=None,
        drive_status="UPCOMING",
        created_at=None
    ):
        self.drive_id = drive_id
        self.company_id = company_id
        self.drive_title = drive_title
        self.drive_date = str(drive_date)
        self.job_role = job_role
        self.job_location = job_location
        self.package_in_lpa = float(package_in_lpa) if package_in_lpa is not None else 0.0
        self.role_description = role_description
        self.minimum_cgpa = float(minimum_cgpa) if minimum_cgpa is not None else None
        self.minimum_10th_percentage = float(minimum_10th_percentage) if minimum_10th_percentage is not None else None
        self.minimum_12th_percentage = float(minimum_12th_percentage) if minimum_12th_percentage is not None else None
        self.maximum_backlogs = int(maximum_backlogs or 0)
        self.eligible_degree = eligible_degree
        self.eligible_branch = eligible_branch
        self.application_deadline = str(application_deadline) if application_deadline else None
        self.created_by = created_by
        self.drive_status = drive_status.upper() if drive_status in self.VALID_STATUSES else "UPCOMING"
        self.created_at = created_at

    @property
    def is_open(self):
        return self.drive_status == "OPEN"

    def check_student_eligibility(self, cgpa=None, tenth_pct=None, twelfth_pct=None, active_backlogs=0):
        """Advanced eligibility evaluation function."""
        if self.minimum_cgpa and (cgpa is None or cgpa < self.minimum_cgpa):
            return False, f"CGPA {cgpa} is below minimum requirement of {self.minimum_cgpa}"
        if self.minimum_10th_percentage and (tenth_pct is None or tenth_pct < self.minimum_10th_percentage):
            return False, f"10th % {tenth_pct} is below minimum requirement of {self.minimum_10th_percentage}%"
        if self.minimum_12th_percentage and (twelfth_pct is None or twelfth_pct < self.minimum_12th_percentage):
            return False, f"12th % {twelfth_pct} is below minimum requirement of {self.minimum_12th_percentage}%"
        if active_backlogs > self.maximum_backlogs:
            return False, f"Active backlogs ({active_backlogs}) exceed allowed maximum ({self.maximum_backlogs})"
        return True, "Eligible"

    def to_dict(self):
        return {
            "drive_id": self.drive_id,
            "company_id": self.company_id,
            "drive_title": self.drive_title,
            "drive_date": self.drive_date,
            "job_role": self.job_role,
            "job_location": self.job_location,
            "package_in_lpa": self.package_in_lpa,
            "role_description": self.role_description,
            "minimum_cgpa": self.minimum_cgpa,
            "minimum_10th_percentage": self.minimum_10th_percentage,
            "minimum_12th_percentage": self.minimum_12th_percentage,
            "maximum_backlogs": self.maximum_backlogs,
            "eligible_degree": self.eligible_degree,
            "eligible_branch": self.eligible_branch,
            "application_deadline": self.application_deadline,
            "drive_status": self.drive_status
        }
