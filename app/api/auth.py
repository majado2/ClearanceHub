from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import RequestOTP, TokenResponse, UserInfo, VerifyOTP
from app.services.auth_service import request_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp")
def request_otp_endpoint(payload: RequestOTP, db: Session = Depends(get_db)):
    request_otp(db, payload.email)
    return {"message": "OTP sent"}


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_endpoint(payload: VerifyOTP, db: Session = Depends(get_db)):
    access_token, refresh_token, user = verify_otp(db, payload.email, payload.otp)
    user_info = UserInfo(role=user.role_code, employee_id=user.employee_id, email=user.internal_email)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role_code,
        "employee_id": user.employee_id,
        "email": user.internal_email,
        "user": user_info,
    }


@router.get("/me", response_model=UserInfo)
def get_me(user=Depends(get_current_user)):
    return UserInfo(role=user.role_code, employee_id=user.employee_id, email=user.internal_email)
