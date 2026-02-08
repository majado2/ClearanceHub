from sqlalchemy import Column, DateTime, BigInteger, Enum, Index, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        Index("idx_employees_department", "department_id"),
        Index("idx_employees_status", "account_status"),
    )

    med_id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), unique=True, nullable=False)
    name_ar = Column(String(150), nullable=False)
    name_en = Column(String(150), nullable=False)
    job_title = Column(String(120), nullable=False)
    nationality_ar = Column(String(120), nullable=False)
    nationality_en = Column(String(120), nullable=False)
    department_id = Column(Integer, nullable=False)
    department_name = Column(String(150), nullable=False)
    account_status = Column(Enum("ACTIVE", "SUSPENDED"), nullable=False, server_default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    permissions = relationship("EmployeePermission", back_populates="employee")
