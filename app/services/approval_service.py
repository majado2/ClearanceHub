from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.card_request import CardRequest
from app.models.permit_request import PermitRequest
from app.services.auth_service import AuthUser
from app.services.request_service import (
    ROLE_CARD_PRINTING,
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_SECURITY,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_IN_PROCESS,
    STATUS_PENDING_MANAGER,
    STATUS_PENDING_SECURITY,
    STATUS_REJECTED_MANAGER,
    STATUS_REJECTED_SECURITY,
    TERMINAL_STATUSES,
)
from app.utils.audit import log_audit


def _now() -> datetime:
    return datetime.utcnow()


def _ensure_manager_scope(db: Session, user: AuthUser, employee_id: str) -> None:
    manager = db.query(Employee).filter(Employee.employee_id == user.employee_id).first()
    target = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not manager or not target or manager.department_id != target.department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def approve_request(
    db: Session, request_type: str, request_obj: CardRequest | PermitRequest, user: AuthUser
):
    if request_obj.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request completed")

    if user.role_code in ROLE_MANAGER:
        if request_obj.status != STATUS_PENDING_MANAGER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        _ensure_manager_scope(db, user, request_obj.employee_id)
        request_obj.status = STATUS_PENDING_SECURITY
        request_obj.manager_employee_id = user.employee_id
        request_obj.manager_updated_at = _now()
        request_obj.rejection_reason = None
    elif user.role_code in ROLE_SECURITY:
        if request_obj.status != STATUS_PENDING_SECURITY:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        request_obj.status = STATUS_IN_PROCESS
        request_obj.security_employee_id = user.employee_id
        request_obj.security_updated_at = _now()
        request_obj.rejection_reason = None
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    entity_type = "card_request" if request_type == "CARD" else "permit_request"
    log_audit(
        db,
        entity_type=entity_type,
        entity_id=request_obj.id,
        action="APPROVED",
        performed_by_email=user.internal_email,
        metadata={"role": user.role_code},
    )

    db.commit()
    db.refresh(request_obj)
    return request_obj


def reject_request(
    db: Session, request_type: str, request_obj: CardRequest | PermitRequest, user: AuthUser, reason: str
):
    if not reason:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rejection reason required")
    if request_obj.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request completed")

    if user.role_code in ROLE_MANAGER:
        if request_obj.status != STATUS_PENDING_MANAGER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        _ensure_manager_scope(db, user, request_obj.employee_id)
        request_obj.status = STATUS_REJECTED_MANAGER
        request_obj.manager_employee_id = user.employee_id
        request_obj.manager_updated_at = _now()
    elif user.role_code in ROLE_SECURITY:
        if request_obj.status != STATUS_PENDING_SECURITY:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        request_obj.status = STATUS_REJECTED_SECURITY
        request_obj.security_employee_id = user.employee_id
        request_obj.security_updated_at = _now()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    request_obj.rejection_reason = reason

    entity_type = "card_request" if request_type == "CARD" else "permit_request"
    log_audit(
        db,
        entity_type=entity_type,
        entity_id=request_obj.id,
        action="REJECTED",
        performed_by_email=user.internal_email,
        metadata={"role": user.role_code, "reason": reason},
    )

    db.commit()
    db.refresh(request_obj)
    return request_obj


def complete_request(
    db: Session, request_type: str, request_obj: CardRequest | PermitRequest, user: AuthUser
):
    if user.role_code not in ROLE_CARD_PRINTING:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if request_obj.status != STATUS_IN_PROCESS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    request_obj.status = STATUS_COMPLETED
    request_obj.printing_employee_id = user.employee_id
    request_obj.printing_updated_at = _now()

    entity_type = "card_request" if request_type == "CARD" else "permit_request"
    log_audit(
        db,
        entity_type=entity_type,
        entity_id=request_obj.id,
        action="COMPLETED",
        performed_by_email=user.internal_email,
    )

    db.commit()
    db.refresh(request_obj)
    return request_obj


def cancel_request(
    db: Session, request_type: str, request_obj: CardRequest | PermitRequest, user: AuthUser, reason: str | None
):
    if user.role_code not in ROLE_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    if request_obj.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Request completed")

    request_obj.status = STATUS_CANCELLED
    if reason:
        request_obj.rejection_reason = reason

    entity_type = "card_request" if request_type == "CARD" else "permit_request"
    log_audit(
        db,
        entity_type=entity_type,
        entity_id=request_obj.id,
        action="CANCELLED",
        performed_by_email=user.internal_email,
        metadata={"reason": reason} if reason else None,
    )

    db.commit()
    db.refresh(request_obj)
    return request_obj
