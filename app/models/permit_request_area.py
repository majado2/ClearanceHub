from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class PermitRequestArea(Base):
    __tablename__ = "permit_request_areas"
    __table_args__ = (UniqueConstraint("permit_request_id", "area_id"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    permit_request_id = Column(BigInteger, ForeignKey("permit_requests.id", ondelete="CASCADE"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.area_id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
