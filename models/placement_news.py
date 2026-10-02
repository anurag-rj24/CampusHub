class PlacementNews:
    """Represents a placement drive announcement or recruitment bulletin."""

    VALID_TARGETS = ("STUDENT", "FACULTY", "ADMIN", "ALL")

    def __init__(
        self,
        news_id,
        title,
        news_description,
        company_id=None,
        drive_id=None,
        published_by=None,
        target_role="STUDENT",
        published_date=None,
        valid_till=None,
        is_active=True,
        created_at=None
    ):
        self.news_id = news_id
        self.title = title
        self.news_description = news_description
        self.company_id = company_id
        self.drive_id = drive_id
        self.published_by = published_by
        self.target_role = target_role.upper() if target_role in self.VALID_TARGETS else "STUDENT"
        self.published_date = str(published_date) if published_date else None
        self.valid_till = str(valid_till) if valid_till else None
        self.is_active = bool(is_active)
        self.created_at = created_at

    def to_dict(self):
        return {
            "news_id": self.news_id,
            "title": self.title,
            "news_description": self.news_description,
            "company_id": self.company_id,
            "drive_id": self.drive_id,
            "published_by": self.published_by,
            "target_role": self.target_role,
            "published_date": self.published_date,
            "valid_till": self.valid_till,
            "is_active": self.is_active
        }
