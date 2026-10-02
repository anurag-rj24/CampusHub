class Notice:
    """Represents a campus announcement or administrative notice."""

    VALID_TARGETS = ("STUDENT", "FACULTY", "ADMIN", "ALL")

    def __init__(self, notice_id, title, content, release_date, valid_till=None, target_role="ALL", created_by=None, is_active=True, created_at=None, updated_at=None):
        self.notice_id = notice_id
        self.title = title
        self.content = content
        self.release_date = str(release_date)
        self.valid_till = str(valid_till) if valid_till else None
        self.target_role = target_role.upper() if target_role in self.VALID_TARGETS else "ALL"
        self.created_by = created_by
        self.is_active = bool(is_active)
        self.created_at = created_at
        self.updated_at = updated_at

    def is_visible_to(self, role):
        if not self.is_active:
            return False
        return self.target_role in ("ALL", role.upper())

    def to_dict(self):
        return {
            "notice_id": self.notice_id,
            "title": self.title,
            "content": self.content,
            "release_date": self.release_date,
            "valid_till": self.valid_till,
            "target_role": self.target_role,
            "created_by": self.created_by,
            "is_active": self.is_active
        }

    def display_info(self):
        print(f"[{self.notice_id}] {self.title} (Target: {self.target_role})")
        print(f"Released: {self.release_date} | Valid Till: {self.valid_till or 'Ongoing'}")
        print("--------------------------------------------------")
        print(self.content)
