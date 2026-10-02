class LeaveRequest:
    """Represents a leave application submitted by a student or staff member."""

    VALID_LEAVE_TYPES = ("CASUAL", "MEDICAL", "ACADEMIC", "OTHER")
    VALID_STATUSES = ("INITIAL_STAGE", "PROCESSING", "APPROVED", "REJECTED")

    def __init__(
        self,
        request_id,
        user_id,
        from_date,
        to_date,
        reason,
        leave_type="CASUAL",
        curr_status="INITIAL_STAGE",
        reviewed_by=None,
        reviewer_comment=None,
        applied_at=None,
        reviewed_at=None,
        updated_at=None
    ):
        self.request_id = request_id
        self.user_id = user_id
        self.from_date = str(from_date)
        self.to_date = str(to_date)
        self.reason = reason
        self.leave_type = leave_type.upper() if leave_type in self.VALID_LEAVE_TYPES else "CASUAL"
        self.curr_status = curr_status.upper() if curr_status in self.VALID_STATUSES else "INITIAL_STAGE"
        self.reviewed_by = reviewed_by
        self.reviewer_comment = reviewer_comment
        self.applied_at = applied_at
        self.reviewed_at = reviewed_at
        self.updated_at = updated_at

    @property
    def is_pending(self):
        return self.curr_status in ("INITIAL_STAGE", "PROCESSING")

    @property
    def is_approved(self):
        return self.curr_status == "APPROVED"

    @property
    def is_rejected(self):
        return self.curr_status == "REJECTED"

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "reason": self.reason,
            "leave_type": self.leave_type,
            "curr_status": self.curr_status,
            "reviewed_by": self.reviewed_by,
            "reviewer_comment": self.reviewer_comment,
            "applied_at": str(self.applied_at) if self.applied_at else None,
            "reviewed_at": str(self.reviewed_at) if self.reviewed_at else None
        }
