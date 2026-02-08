from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, conlist

from app.schemas.area import AreaRead
from app.schemas.employee import EmployeeRead, EmployeeSnapshot


class CardRequestCreate(BaseModel):
    employee_id: str
    request_type: Literal["NEW", "RENEW", "REPLACE_LOST"]
    request_reason: Optional[str] = None
    photo_url: Optional[str] = None


class PermitRequestCreate(BaseModel):
    employee_id: str
    area_ids: conlist(int, min_length=1)
    request_reason: Optional[str] = None


class CardRequestRead(BaseModel):
    id: int
    employee_id: str
    submitted_by_employee_id: Optional[str] = None
    request_date: datetime
    request_type: str
    request_reason: Optional[str] = None
    photo_url: Optional[str] = None
    manager_employee_id: Optional[str] = None
    manager_updated_at: Optional[datetime] = None
    security_employee_id: Optional[str] = None
    security_updated_at: Optional[datetime] = None
    printing_employee_id: Optional[str] = None
    printing_updated_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PermitRequestRead(BaseModel):
    id: int
    employee_id: str
    submitted_by_employee_id: Optional[str] = None
    request_date: datetime
    request_reason: Optional[str] = None
    manager_employee_id: Optional[str] = None
    manager_updated_at: Optional[datetime] = None
    security_employee_id: Optional[str] = None
    security_updated_at: Optional[datetime] = None
    printing_employee_id: Optional[str] = None
    printing_updated_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    area_ids: List[int] = Field(default_factory=list)
    areas: List[AreaRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class ApprovalTimelineItem(BaseModel):
    role: str
    employee_id: str
    action: str
    updated_at: datetime


class RequestDetailResponse(BaseModel):
    request_type: Literal["CARD", "ACCESS"]
    employee: EmployeeSnapshot
    card_request: Optional[CardRequestRead] = None
    permit_request: Optional[PermitRequestRead] = None
    approvals: List[ApprovalTimelineItem] = Field(default_factory=list)


class RequestListItem(BaseModel):
    id: int
    request_type: Literal["CARD", "ACCESS"]
    employee_id: str
    submitted_by_employee_id: Optional[str] = None
    status: str
    request_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    card_request_type: Optional[str] = None
    employee: Optional[EmployeeRead] = None


class RequestListResponse(BaseModel):
    items: List[RequestListItem]
    total: int
