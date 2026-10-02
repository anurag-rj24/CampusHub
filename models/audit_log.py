class AuditLog:
    """Represents an immutable system security and activity audit entry."""

    VALID_ACTIONS = ("LOGIN", "LOGOUT", "INSERT", "UPDATE", "DELETE", "APPROVE", "REJECT", "VIEW")

    def __init__(self, log_id, user_id, action, table_name=None, record_id=None, description=None, ip_address="127.0.0.1", created_at=None):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action.upper() if action in self.VALID_ACTIONS else "VIEW"
        self.table_name = table_name
        self.record_id = record_id
        self.description = description
        self.ip_address = ip_address
        self.created_at = created_at

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "action": self.action,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "description": self.description,
            "ip_address": self.ip_address,
            "created_at": str(self.created_at) if self.created_at else None
        }

    def __str__(self):
        return f"[{self.created_at}] User #{self.user_id} -> {self.action} on {self.table_name or 'System'} (ID: {self.record_id or 'N/A'})"
