from datetime import date, datetime, time
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.area import Area
from app.models.card_request import CardRequest
from app.models.employee import Employee
from app.models.permit_request import PermitRequest
from app.models.permit_request_area import PermitRequestArea
from app.services.auth_service import AuthUser
from app.utils.audit import log_audit

STATUS_DRAFT = "DRAFT"
STATUS_PENDING_MANAGER = "PENDING_MANAGER_APPROVAL"
STATUS_REJECTED_MANAGER = "REJECTED_BY_MANAGER"
STATUS_PENDING_SECURITY = "PENDING_SECURITY_APPROVAL"
STATUS_REJECTED_SECURITY = "REJECTED_BY_SECURITY"
STATUS_IN_PROCESS = "IN_PROCESS"
STATUS_COMPLETED = "COMPLETED"
STATUS_CANCELLED = "CANCELLED"

TERMINAL_STATUSES = {STATUS_COMPLETED, STATUS_CANCELLED}
PRINTING_VISIBLE_STATUSES = {STATUS_IN_PROCESS, STATUS_COMPLETED}
PENDING_STATUSES = {STATUS_PENDING_MANAGER, STATUS_PENDING_SECURITY}
APPROVED_STATUSES = {STATUS_IN_PROCESS, STATUS_COMPLETED}
REJECTED_STATUSES = {STATUS_REJECTED_MANAGER, STATUS_REJECTED_SECURITY}

ROLE_MANAGER = {"DEPT_MANAGER", "MANAGER"}
ROLE_SECURITY = {"SECURITY_OFFICER", "SECURITY"}
ROLE_CARD_PRINTING = {"CARD_PRINTING"}
ROLE_ADMIN = {"ADMIN", "SYSTEM_ADMIN"}

STAFF_ROLES = ROLE_MANAGER | ROLE_SECURITY | ROLE_CARD_PRINTING | ROLE_ADMIN


def _normalize_request_type(request_type: Optional[str]) -> Optional[str]:
    if not request_type:
        return None
    value = request_type.strip().upper()
    if value in {"CARD", "ACCESS"}:
        return value
    if value in {"PERMIT", "ACCESS_REQUEST"}:
        return "ACCESS"
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request type")


def _get_employee(db: Session, employee_id: str, active_only: bool = True) -> Employee:
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    if active_only and employee.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


def _get_manager_department_id(db: Session, user: AuthUser) -> int:
    manager = _get_employee(db, user.employee_id, active_only=True)
    return manager.department_id


def _get_manager_department_info(db: Session, user: AuthUser) -> tuple[int, str]:
    manager = _get_employee(db, user.employee_id, active_only=True)
    return manager.department_id, manager.department_name


def _ensure_manager_scope(db: Session, user: AuthUser, employee_id: str) -> None:
    manager_department_id = _get_manager_department_id(db, user)
    target_employee = _get_employee(db, employee_id, active_only=True)
    if target_employee.department_id != manager_department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def _ensure_staff_access(db: Session, user: AuthUser, employee_id: str) -> None:
    if user.role_code in ROLE_MANAGER:
        _ensure_manager_scope(db, user, employee_id)


def _apply_date_filter(query, model, date_from: Optional[date], date_to: Optional[date]):
    if date_from:
        if isinstance(date_from, datetime):
            from_dt = date_from
        else:
            from_dt = datetime.combine(date_from, time.min)
        query = query.filter(model.request_date >= from_dt)
    if date_to:
        if isinstance(date_to, datetime):
            to_dt = date_to
        else:
            to_dt = datetime.combine(date_to, time.max)
        query = query.filter(model.request_date <= to_dt)
    return query


def create_card_request(db: Session, payload: dict, user: AuthUser | None) -> CardRequest:
    employee_id = payload["employee_id"]
    _get_employee(db, employee_id, active_only=True)

    submitted_by = None
    if user:
        if user.role_code in ROLE_MANAGER:
            _ensure_manager_scope(db, user, employee_id)
        elif user.role_code not in ROLE_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        submitted_by = user.employee_id

    card = CardRequest(
        employee_id=employee_id,
        submitted_by_employee_id=submitted_by,
        request_type=payload["request_type"],
        request_reason=payload.get("request_reason"),
        photo_url=payload.get("photo_url"),
        status=STATUS_PENDING_MANAGER,
    )
    db.add(card)
    db.flush()

    log_audit(
        db,
        entity_type="card_request",
        entity_id=card.id,
        action="CREATED",
        performed_by_email=user.internal_email if user else None,
        metadata={"request_type": "CARD", "employee_id": employee_id},
    )

    db.commit()
    db.refresh(card)
    return card


def create_permit_request(db: Session, payload: dict, user: AuthUser | None) -> PermitRequest:
    employee_id = payload["employee_id"]
    area_ids = list(dict.fromkeys(payload["area_ids"]))
    if not area_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="area_ids required")

    _get_employee(db, employee_id, active_only=True)

    submitted_by = None
    if user:
        if user.role_code in ROLE_MANAGER:
            _ensure_manager_scope(db, user, employee_id)
        elif user.role_code not in ROLE_ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        submitted_by = user.employee_id

    areas = (
        db.query(Area)
        .filter(Area.area_id.in_(area_ids), Area.status == "ACTIVE")
        .all()
    )
    if len(areas) != len(area_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid area_ids")

    permit = PermitRequest(
        employee_id=employee_id,
        submitted_by_employee_id=submitted_by,
        request_reason=payload.get("request_reason"),
        status=STATUS_PENDING_MANAGER,
    )
    db.add(permit)
    db.flush()

    for area_id in area_ids:
        db.add(PermitRequestArea(permit_request_id=permit.id, area_id=area_id))

    log_audit(
        db,
        entity_type="permit_request",
        entity_id=permit.id,
        action="CREATED",
        performed_by_email=user.internal_email if user else None,
        metadata={"request_type": "ACCESS", "employee_id": employee_id, "area_ids": area_ids},
    )

    db.commit()
    db.refresh(permit)
    return permit


def get_request_by_id(
    db: Session, request_id: int, request_type: Optional[str] = None
) -> tuple[str, CardRequest | PermitRequest]:
    normalized = _normalize_request_type(request_type)

    if normalized == "CARD":
        card = db.query(CardRequest).filter(CardRequest.id == request_id).first()
        if not card:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        return "CARD", card

    if normalized == "ACCESS":
        permit = db.query(PermitRequest).filter(PermitRequest.id == request_id).first()
        if not permit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        return "ACCESS", permit

    card = db.query(CardRequest).filter(CardRequest.id == request_id).first()
    permit = db.query(PermitRequest).filter(PermitRequest.id == request_id).first()
    if card and permit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambiguous request id")
    if card:
        return "CARD", card
    if permit:
        return "ACCESS", permit
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")


def _build_approvals_timeline(request_obj) -> list[dict]:
    timeline = []
    if request_obj.manager_employee_id and request_obj.manager_updated_at:
        action = "REJECTED" if request_obj.status == STATUS_REJECTED_MANAGER else "APPROVED"
        timeline.append(
            {
                "role": "MANAGER",
                "employee_id": request_obj.manager_employee_id,
                "action": action,
                "updated_at": request_obj.manager_updated_at,
            }
        )
    if request_obj.security_employee_id and request_obj.security_updated_at:
        action = "REJECTED" if request_obj.status == STATUS_REJECTED_SECURITY else "APPROVED"
        timeline.append(
            {
                "role": "SECURITY",
                "employee_id": request_obj.security_employee_id,
                "action": action,
                "updated_at": request_obj.security_updated_at,
            }
        )
    if request_obj.printing_employee_id and request_obj.printing_updated_at:
        timeline.append(
            {
                "role": "CARD_PRINTING",
                "employee_id": request_obj.printing_employee_id,
                "action": "COMPLETED",
                "updated_at": request_obj.printing_updated_at,
            }
        )
    return sorted(timeline, key=lambda item: item["updated_at"])


def get_request_detail(
    db: Session,
    request_id: int,
    request_type: Optional[str],
    user: AuthUser,
) -> dict:
    request_kind, request_obj = get_request_by_id(db, request_id, request_type)
    _ensure_staff_access(db, user, request_obj.employee_id)
    if user.role_code in ROLE_CARD_PRINTING and request_obj.status not in PRINTING_VISIBLE_STATUSES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    employee = _get_employee(db, request_obj.employee_id, active_only=False)
    approvals = _build_approvals_timeline(request_obj)

    if request_kind == "CARD":
        return {
            "request_type": "CARD",
            "employee": employee,
            "card_request": request_obj,
            "permit_request": None,
            "approvals": approvals,
        }

    area_links = (
        db.query(PermitRequestArea)
        .filter(PermitRequestArea.permit_request_id == request_obj.id)
        .all()
    )
    area_ids = [link.area_id for link in area_links]
    areas = db.query(Area).filter(Area.area_id.in_(area_ids)).order_by(Area.area_name).all() if area_ids else []

    permit_data = {
        "id": request_obj.id,
        "employee_id": request_obj.employee_id,
        "submitted_by_employee_id": request_obj.submitted_by_employee_id,
        "request_date": request_obj.request_date,
        "request_reason": request_obj.request_reason,
        "manager_employee_id": request_obj.manager_employee_id,
        "manager_updated_at": request_obj.manager_updated_at,
        "security_employee_id": request_obj.security_employee_id,
        "security_updated_at": request_obj.security_updated_at,
        "printing_employee_id": request_obj.printing_employee_id,
        "printing_updated_at": request_obj.printing_updated_at,
        "rejection_reason": request_obj.rejection_reason,
        "status": request_obj.status,
        "created_at": request_obj.created_at,
        "updated_at": request_obj.updated_at,
        "area_ids": area_ids,
        "areas": areas,
    }

    return {
        "request_type": "ACCESS",
        "employee": employee,
        "card_request": None,
        "permit_request": permit_data,
        "approvals": approvals,
    }


def list_requests(
    db: Session,
    request_type: Optional[str] = None,
    status_value: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    user: AuthUser | None = None,
) -> list[dict]:
    normalized = _normalize_request_type(request_type)
    normalized_status = status_value.strip().upper() if status_value else None

    manager_department_id = None
    if user and user.role_code in ROLE_MANAGER:
        manager_department_id = _get_manager_department_id(db, user)

    items: list[dict] = []

    if normalized in {None, "CARD"}:
        query = db.query(CardRequest)
        if normalized_status:
            query = query.filter(CardRequest.status == normalized_status)
        if user and user.role_code in ROLE_CARD_PRINTING:
            query = query.filter(CardRequest.status.in_(PRINTING_VISIBLE_STATUSES))
        query = _apply_date_filter(query, CardRequest, date_from, date_to)
        if manager_department_id is not None:
            query = query.join(Employee, CardRequest.employee_id == Employee.employee_id).filter(
                Employee.department_id == manager_department_id
            )
        cards = query.all()
        for card in cards:
            items.append(
                {
                    "id": card.id,
                    "request_type": "CARD",
                    "employee_id": card.employee_id,
                    "submitted_by_employee_id": card.submitted_by_employee_id,
                    "status": card.status,
                    "request_date": card.request_date,
                    "created_at": card.created_at,
                    "updated_at": card.updated_at,
                    "card_request_type": card.request_type,
                }
            )

    if normalized in {None, "ACCESS"}:
        query = db.query(PermitRequest)
        if normalized_status:
            query = query.filter(PermitRequest.status == normalized_status)
        if user and user.role_code in ROLE_CARD_PRINTING:
            query = query.filter(PermitRequest.status.in_(PRINTING_VISIBLE_STATUSES))
        query = _apply_date_filter(query, PermitRequest, date_from, date_to)
        if manager_department_id is not None:
            query = query.join(Employee, PermitRequest.employee_id == Employee.employee_id).filter(
                Employee.department_id == manager_department_id
            )
        permits = query.all()
        for permit in permits:
            items.append(
                {
                    "id": permit.id,
                    "request_type": "ACCESS",
                    "employee_id": permit.employee_id,
                    "submitted_by_employee_id": permit.submitted_by_employee_id,
                    "status": permit.status,
                    "request_date": permit.request_date,
                    "created_at": permit.created_at,
                    "updated_at": permit.updated_at,
                    "card_request_type": None,
                }
            )

    items.sort(key=lambda item: item["request_date"], reverse=True)
    employee_ids = list({item["employee_id"] for item in items})
    employees = {}
    if employee_ids:
        employee_rows = db.query(Employee).filter(Employee.employee_id.in_(employee_ids)).all()
        employees = {row.employee_id: row for row in employee_rows}

    for item in items:
        item["employee"] = employees.get(item["employee_id"])

    return items


def _aggregate_counts(
    items: list[dict],
    pending_statuses: set[str],
    approved_statuses: set[str],
    rejected_statuses: set[str],
) -> dict:
    counts = {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
    for item in items:
        counts["total"] += 1
        status = item.get("status")
        if status in pending_statuses:
            counts["pending"] += 1
        elif status in approved_statuses:
            counts["approved"] += 1
        elif status in rejected_statuses:
            counts["rejected"] += 1
    return counts


def get_dashboard_summary(
    db: Session,
    user: AuthUser,
) -> dict:
    all_items = list_requests(db, request_type=None, status_value=None, date_from=None, date_to=None, user=user)
    card_items = [item for item in all_items if item["request_type"] == "CARD"]
    access_items = [item for item in all_items if item["request_type"] == "ACCESS"]

    pending_statuses = PENDING_STATUSES
    approved_statuses = APPROVED_STATUSES
    rejected_statuses = REJECTED_STATUSES

    if user.role_code in ROLE_CARD_PRINTING:
        pending_statuses = {STATUS_IN_PROCESS}
        approved_statuses = {STATUS_COMPLETED}
        rejected_statuses = set()

    if user.role_code in ROLE_MANAGER:
        department_id, department_name = _get_manager_department_info(db, user)
        scope = {"type": "DEPARTMENT", "department_id": department_id, "department_name": department_name}
    else:
        scope = {"type": "ALL", "department_id": None, "department_name": None}

    return {
        "scope": scope,
        "all": _aggregate_counts(all_items, pending_statuses, approved_statuses, rejected_statuses),
        "card": _aggregate_counts(card_items, pending_statuses, approved_statuses, rejected_statuses),
        "access": _aggregate_counts(access_items, pending_statuses, approved_statuses, rejected_statuses),
    }


def get_request_export_rows(
    db: Session,
    request_type: Optional[str],
    status_value: Optional[str],
    date_from: Optional[date],
    date_to: Optional[date],
    user: AuthUser,
) -> list[dict]:
    items = list_requests(
        db,
        request_type=request_type,
        status_value=status_value,
        date_from=date_from,
        date_to=date_to,
        user=user,
    )

    card_ids = [item["id"] for item in items if item["request_type"] == "CARD"]
    permit_ids = [item["id"] for item in items if item["request_type"] == "ACCESS"]
    employee_ids = list({item["employee_id"] for item in items})

    cards = {}
    if card_ids:
        card_rows = db.query(CardRequest).filter(CardRequest.id.in_(card_ids)).all()
        cards = {row.id: row for row in card_rows}

    permits = {}
    if permit_ids:
        permit_rows = db.query(PermitRequest).filter(PermitRequest.id.in_(permit_ids)).all()
        permits = {row.id: row for row in permit_rows}

    employees = {}
    if employee_ids:
        employee_rows = db.query(Employee).filter(Employee.employee_id.in_(employee_ids)).all()
        employees = {row.employee_id: row for row in employee_rows}

    permit_area_ids: dict[int, list[int]] = {}
    permit_area_names: dict[int, list[str]] = {}
    if permit_ids:
        area_rows = (
            db.query(PermitRequestArea.permit_request_id, Area.area_id, Area.area_name)
            .join(Area, PermitRequestArea.area_id == Area.area_id)
            .filter(PermitRequestArea.permit_request_id.in_(permit_ids))
            .order_by(PermitRequestArea.permit_request_id, Area.area_name)
            .all()
        )
        for permit_id, area_id, area_name in area_rows:
            permit_area_ids.setdefault(permit_id, []).append(area_id)
            permit_area_names.setdefault(permit_id, []).append(area_name)

    rows: list[dict] = []
    for item in items:
        employee = employees.get(item["employee_id"])

        base = {
            "request_id": item["id"],
            "request_type": item["request_type"],
            "status": item["status"],
            "request_date": item["request_date"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "submitted_by_employee_id": item["submitted_by_employee_id"],
            "employee_id": item["employee_id"],
            "employee_name_ar": getattr(employee, "name_ar", None),
            "employee_name_en": getattr(employee, "name_en", None),
            "job_title": getattr(employee, "job_title", None),
            "nationality_ar": getattr(employee, "nationality_ar", None),
            "nationality_en": getattr(employee, "nationality_en", None),
            "department_id": getattr(employee, "department_id", None),
            "department_name": getattr(employee, "department_name", None),
            "account_status": getattr(employee, "account_status", None),
        }

        if item["request_type"] == "CARD":
            card = cards.get(item["id"])
            rows.append(
                {
                    **base,
                    "card_request_type": getattr(card, "request_type", None),
                    "card_request_reason": getattr(card, "request_reason", None),
                    "photo_url": getattr(card, "photo_url", None),
                    "permit_request_reason": None,
                    "permit_area_ids": None,
                    "permit_area_names": None,
                    "manager_employee_id": getattr(card, "manager_employee_id", None),
                    "manager_updated_at": getattr(card, "manager_updated_at", None),
                    "security_employee_id": getattr(card, "security_employee_id", None),
                    "security_updated_at": getattr(card, "security_updated_at", None),
                    "printing_employee_id": getattr(card, "printing_employee_id", None),
                    "printing_updated_at": getattr(card, "printing_updated_at", None),
                    "rejection_reason": getattr(card, "rejection_reason", None),
                }
            )
        else:
            permit = permits.get(item["id"])
            rows.append(
                {
                    **base,
                    "card_request_type": None,
                    "card_request_reason": None,
                    "photo_url": None,
                    "permit_request_reason": getattr(permit, "request_reason", None),
                    "permit_area_ids": permit_area_ids.get(item["id"], []),
                    "permit_area_names": permit_area_names.get(item["id"], []),
                    "manager_employee_id": getattr(permit, "manager_employee_id", None),
                    "manager_updated_at": getattr(permit, "manager_updated_at", None),
                    "security_employee_id": getattr(permit, "security_employee_id", None),
                    "security_updated_at": getattr(permit, "security_updated_at", None),
                    "printing_employee_id": getattr(permit, "printing_employee_id", None),
                    "printing_updated_at": getattr(permit, "printing_updated_at", None),
                    "rejection_reason": getattr(permit, "rejection_reason", None),
                }
            )

    return rows
