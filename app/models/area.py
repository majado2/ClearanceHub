from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class Area(Base):
    __tablename__ = "areas"

    area_id = Column(Integer, primary_key=True, autoincrement=True)
    area_name = Column(String(150), nullable=False)
    status = Column(Enum("ACTIVE", "INACTIVE"), nullable=False, server_default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())
