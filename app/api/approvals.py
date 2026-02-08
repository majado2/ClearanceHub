from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.schemas.approval import CancelRequest, RejectRequest
from app.services.approval_service import approve_request, cancel_request, complete_request, reject_request
from app.services.request_service import get_request_by_id

router = APIRouter(prefix="/requests", tags=["approvals"])


@router.post("/{request_id}/approve")
def approve_request_endpoint(
    request_id: int,
    request_type: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    request_kind, request_obj = get_request_by_id(db, request_id, request_type)
    request_obj = approve_request(db, request_kind, request_obj, user)
    return {"id": request_obj.id, "status": request_obj.status}


@router.post("/{request_id}/reject")
def reject_request_endpoint(
    request_id: int,
    payload: RejectRequest,
    request_type: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    request_kind, request_obj = get_request_by_id(db, request_id, request_type)
    request_obj = reject_request(db, request_kind, request_obj, user, payload.reason)
    return {"id": request_obj.id, "status": request_obj.status}


@router.post("/{request_id}/complete")
def complete_request_endpoint(
    request_id: int,
    request_type: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    request_kind, request_obj = get_request_by_id(db, request_id, request_type)
    request_obj = complete_request(db, request_kind, request_obj, user)
    return {"id": request_obj.id, "status": request_obj.status}


@router.post("/{request_id}/cancel")
def cancel_request_endpoint(
    request_id: int,
    payload: CancelRequest,
    request_type: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    request_kind, request_obj = get_request_by_id(db, request_id, request_type)
    request_obj = cancel_request(db, request_kind, request_obj, user, payload.reason)
    return {"id": request_obj.id, "status": request_obj.status}
