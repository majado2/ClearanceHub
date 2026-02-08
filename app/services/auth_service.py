import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.auth_token import AuthToken
from app.models.employee import Employee
from app.models.employee_permission import EmployeePermission
from app.models.role import Role
from app.models.user_otp import UserOTP
from app.utils.email import send_email
from app.utils.otp import generate_otp
from app.utils.otp_email import build_otp_email


class AuthError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


@dataclass(frozen=True)
class AuthUser:
    internal_email: str
    employee_id: str
    role_code: str


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user: AuthUser) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user.internal_email,
        "role": user.role_code,
        "employee_id": user.employee_id,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user: AuthUser) -> tuple[str, datetime]:
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user.internal_email,
        "role": user.role_code,
        "employee_id": user.employee_id,
        "type": "refresh",
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, expire


def _get_permission_by_email(db: Session, email: str) -> EmployeePermission | None:
    return (
        db.query(EmployeePermission)
        .join(Role, EmployeePermission.role_id == Role.id)
        .filter(EmployeePermission.internal_email == email, EmployeePermission.is_active.is_(True))
        .first()
    )


def _get_permission_by_employee_id(db: Session, employee_id: str) -> EmployeePermission | None:
    return (
        db.query(EmployeePermission)
        .join(Role, EmployeePermission.role_id == Role.id)
        .filter(EmployeePermission.employee_id == employee_id, EmployeePermission.is_active.is_(True))
        .first()
    )


def _resolve_permission(db: Session, identifier: str) -> tuple[EmployeePermission, str]:
    identifier = identifier.strip()
    if "@" in identifier:
        permission = _get_permission_by_email(db, identifier)
        email = identifier
    else:
        permission = _get_permission_by_employee_id(db, identifier)
        email = permission.internal_email if permission else ""
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return permission, email


def _ensure_employee_active(db: Session, employee_id: str) -> None:
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee or employee.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")


def request_otp(db: Session, identifier: str) -> str:
    permission, email = _resolve_permission(db, identifier)
    _ensure_employee_active(db, permission.employee_id)

    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)

    otp = UserOTP(internal_email=email, otp_code=otp_code, expires_at=expires_at, is_used=False)
    db.add(otp)
    db.commit()

    subject, text_body, html_body = build_otp_email(otp_code)
    try:
        send_email(email, subject, text_body, html_body)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP") from exc
    return otp_code


def verify_otp(db: Session, identifier: str, otp: str) -> tuple[str, str, AuthUser]:
    permission, email = _resolve_permission(db, identifier)
    _ensure_employee_active(db, permission.employee_id)

    if settings.otp_fixed_enabled:
        if otp != settings.otp_fixed_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    else:
        latest_otp = (
            db.query(UserOTP)
            .filter(UserOTP.internal_email == email, UserOTP.is_used.is_(False))
            .order_by(UserOTP.id.desc())
            .first()
        )
        if not latest_otp or latest_otp.otp_code != otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
        if latest_otp.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")
        latest_otp.is_used = True

    role = db.query(Role).filter(Role.id == permission.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    role_code = role.role_code
    user = AuthUser(internal_email=email, employee_id=permission.employee_id, role_code=role_code)

    access_token = create_access_token(user)
    refresh_token, refresh_exp = create_refresh_token(user)

    token_record = AuthToken(
        internal_email=email,
        token_hash=_hash_token(refresh_token),
        expires_at=refresh_exp,
        revoked=False,
    )
    db.add(token_record)
    db.commit()

    return access_token, refresh_token, user


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthError("Invalid token") from exc
    return payload


def get_user_from_token(db: Session, token: str) -> AuthUser:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise AuthError("Invalid token type")

    email = payload.get("sub")
    if not email:
        raise AuthError("Invalid token")

    permission = _get_permission_by_email(db, email)
    if not permission:
        raise AuthError("User not found")

    role = db.query(Role).filter(Role.id == permission.role_id).first()
    if not role:
        raise AuthError("Role not found")
    role_code = role.role_code

    _ensure_employee_active(db, permission.employee_id)

    return AuthUser(internal_email=email, employee_id=permission.employee_id, role_code=role_code)
