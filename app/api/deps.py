from typing import Callable, Iterable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import get_user_from_token


def _extract_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return token


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    token = _extract_token(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    return get_user_from_token(db, token)


def get_optional_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None),
):
    token = _extract_token(authorization)
    if not token:
        return None
    return get_user_from_token(db, token)


def require_roles(roles: Iterable[str]) -> Callable:
    def _role_guard(user=Depends(get_current_user)):
        if user.role_code not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _role_guard
