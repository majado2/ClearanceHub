from sqlalchemy import Column, BigInteger, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.sql import func

from app.db.database import Base


class CardRequest(Base):
    __tablename__ = "card_requests"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    submitted_by_employee_id = Column(String(50), ForeignKey("employees.employee_id"))
    request_date = Column(DateTime, server_default=func.now(), nullable=False)
    request_type = Column(Enum("NEW", "RENEW", "REPLACE_LOST"), nullable=False)
    request_reason = Column(Text)
    photo_url = Column(Text)

    manager_employee_id = Column(String(50))
    manager_updated_at = Column(DateTime)

    security_employee_id = Column(String(50))
    security_updated_at = Column(DateTime)

    printing_employee_id = Column(String(50))
    printing_updated_at = Column(DateTime)

    rejection_reason = Column(Text)
    status = Column(
        Enum(
            "DRAFT",
            "PENDING_MANAGER_APPROVAL",
            "REJECTED_BY_MANAGER",
            "PENDING_SECURITY_APPROVAL",
            "REJECTED_BY_SECURITY",
            "IN_PROCESS",
            "COMPLETED",
            "CANCELLED",
        ),
        nullable=False,
        server_default="PENDING_MANAGER_APPROVAL",
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
