from pydantic import BaseModel


class UserInfo(BaseModel):
    role: str
    employee_id: str
    email: str


class RequestOTP(BaseModel):
    email: str


class VerifyOTP(BaseModel):
    email: str
    otp: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    employee_id: str
    email: str
    user: UserInfo
