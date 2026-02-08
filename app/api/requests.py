from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_optional_user, require_roles
from app.db.database import get_db
from app.schemas.request import (
    CardRequestCreate,
    PermitRequestCreate,
    RequestDetailResponse,
    RequestListResponse,
)
from app.services.request_service import (
    STAFF_ROLES,
    create_card_request,
    create_permit_request,
    get_request_detail,
    list_requests,
)

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("/card")
def create_card_request_endpoint(
    payload: CardRequestCreate,
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
):
    request = create_card_request(db, payload.model_dump(), user)
    return {"id": request.id, "status": request.status}


@router.post("/access")
def create_access_request_endpoint(
    payload: PermitRequestCreate,
    db: Session = Depends(get_db),
    user=Depends(get_optional_user),
):
    request = create_permit_request(db, payload.model_dump(), user)
    return {"id": request.id, "status": request.status}


@router.get("/{request_id}", response_model=RequestDetailResponse)
def get_request_detail_endpoint(
    request_id: int,
    request_type: Optional[str] = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
    user=Depends(require_roles(STAFF_ROLES)),
):
    return get_request_detail(db, request_id, request_type, user)


@router.get("", response_model=RequestListResponse)
def list_requests_endpoint(
    type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    from_date: Optional[date] = Query(default=None, alias="from"),
    to_date: Optional[date] = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user=Depends(require_roles(STAFF_ROLES)),
):
    items = list_requests(
        db, request_type=type, status_value=status, date_from=from_date, date_to=to_date, user=user
    )
    return {"items": items, "total": len(items)}
