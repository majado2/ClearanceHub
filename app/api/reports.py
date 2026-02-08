from datetime import date
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.database import get_db
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.request_service import STAFF_ROLES, get_dashboard_summary, get_request_export_rows, list_requests
from app.utils.csv_export import requests_to_csv
from app.utils.excel import requests_to_excel

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/requests/excel")
def export_requests_excel(
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
    content = requests_to_excel(items)
    stream = BytesIO(content)
    headers = {"Content-Disposition": "attachment; filename=requests.xlsx"}
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/requests/csv")
def export_requests_csv(
    type: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    from_date: Optional[date] = Query(default=None, alias="from"),
    to_date: Optional[date] = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
    user=Depends(require_roles(STAFF_ROLES)),
):
    rows = get_request_export_rows(
        db,
        request_type=type,
        status_value=status,
        date_from=from_date,
        date_to=to_date,
        user=user,
    )
    headers = [
        "request_id",
        "request_type",
        "status",
        "request_date",
        "created_at",
        "updated_at",
        "submitted_by_employee_id",
        "employee_id",
        "employee_name_ar",
        "employee_name_en",
        "job_title",
        "nationality_ar",
        "nationality_en",
        "department_id",
        "department_name",
        "account_status",
        "card_request_type",
        "card_request_reason",
        "photo_url",
        "permit_request_reason",
        "permit_area_ids",
        "permit_area_names",
        "manager_employee_id",
        "manager_updated_at",
        "security_employee_id",
        "security_updated_at",
        "printing_employee_id",
        "printing_updated_at",
        "rejection_reason",
    ]
    content = requests_to_csv(rows, headers)
    stream = BytesIO(content)
    headers_resp = {"Content-Disposition": "attachment; filename=requests.csv"}
    return StreamingResponse(stream, media_type="text/csv; charset=utf-8", headers=headers_resp)


@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(
    db: Session = Depends(get_db),
    user=Depends(require_roles(STAFF_ROLES)),
):
    return get_dashboard_summary(db, user)
