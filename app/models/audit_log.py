from sqlalchemy import Column, DateTime, BigInteger, String, JSON
from sqlalchemy.sql import func

from app.db.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(BigInteger, nullable=False)
    action = Column(String(100), nullable=False)
    performed_by_email = Column(String(150))
    metadata_json = Column("metadata", JSON)
    created_at = Column(DateTime, server_default=func.now())
