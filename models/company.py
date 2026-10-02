class Company:
    """Represents a recruiting company/partner organisation in the placement module."""

    def __init__(self, company_id, company_name, industry_type, location, company_description=None, website=None, contact_email=None, contact_phone=None):
        self.company_id = company_id
        self.company_name = company_name
        self.industry_type = industry_type
        self.location = location
        self.company_description = company_description
        self.website = website
        self.contact_email = contact_email
        self.contact_phone = contact_phone

    def to_dict(self):
        return {
            "company_id": self.company_id,
            "company_name": self.company_name,
            "industry_type": self.industry_type,
            "location": self.location,
            "company_description": self.company_description,
            "website": self.website,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            company_id=data.get("company_id"),
            company_name=data.get("company_name", ""),
            industry_type=data.get("industry_type", ""),
            location=data.get("location", ""),
            company_description=data.get("company_description"),
            website=data.get("website"),
            contact_email=data.get("contact_email"),
            contact_phone=data.get("contact_phone")
        )

    def display_info(self):
        print(f"Company: {self.company_name} (ID: {self.company_id}) | Industry: {self.industry_type}")
        print(f"Location: {self.location} | Website: {self.website or 'N/A'}")
        print(f"Contact: {self.contact_email or 'N/A'} | {self.contact_phone or 'N/A'}")

    def __str__(self):
        return f"{self.company_name} ({self.industry_type}) - {self.location}"
