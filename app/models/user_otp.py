from sqlalchemy import Boolean, Column, DateTime, BigInteger, String
from sqlalchemy.sql import func

from app.db.database import Base


class UserOTP(Base):
    __tablename__ = "user_otp"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    internal_email = Column(String(150), nullable=False)
    otp_code = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
