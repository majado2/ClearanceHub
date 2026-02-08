from typing import Optional

from pydantic import BaseModel


class RejectRequest(BaseModel):
    reason: str


class CancelRequest(BaseModel):
    reason: Optional[str] = None
