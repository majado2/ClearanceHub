from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_code = Column(String(50), unique=True, nullable=False)
    role_name = Column(String(150), nullable=False)

    permissions = relationship("EmployeePermission", back_populates="role")
