from sqlalchemy import Boolean, Column, DateTime, BigInteger, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class EmployeePermission(Base):
    __tablename__ = "employee_permissions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False, unique=True)
    internal_email = Column(String(150), nullable=False, unique=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    employee = relationship("Employee", back_populates="permissions")
    role = relationship("Role", back_populates="permissions")
