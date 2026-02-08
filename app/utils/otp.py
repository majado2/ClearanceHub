import random

from app.core.config import settings


def generate_otp() -> str:
    if settings.otp_fixed_enabled:
        return settings.otp_fixed_code
    return f"{random.randint(100000, 999999)}"