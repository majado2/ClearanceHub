from typing import Literal, Optional

from pydantic import BaseModel


class DashboardScope(BaseModel):
    type: Literal["ALL", "DEPARTMENT"]
    department_id: Optional[int] = None
    department_name: Optional[str] = None


class DashboardCounts(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class DashboardSummaryResponse(BaseModel):
    scope: DashboardScope
    all: DashboardCounts
    card: DashboardCounts
    access: DashboardCounts
