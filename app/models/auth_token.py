from sqlalchemy import Boolean, Column, DateTime, BigInteger, String
from sqlalchemy.sql import func

from app.db.database import Base


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    internal_email = Column(String(150), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
