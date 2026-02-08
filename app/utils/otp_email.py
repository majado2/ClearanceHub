from app.core.config import settings


def build_otp_email(otp_code: str) -> tuple[str, str, str]:
    subject = "رمز التحقق - ClearanceHub"
    minutes = settings.otp_expire_minutes
    text_body = (
        "مرحبًا،\n\n"
        "رمز التحقق الخاص بك هو:\n"
        f"{otp_code}\n\n"
        f"الرمز صالح لمدة {minutes} دقائق.\n"
        "إذا لم تطلب هذا الرمز، يمكنك تجاهل الرسالة.\n\n"
        "— ClearanceHub"
    )

    html_body = f"""
<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>رمز التحقق</title>
  </head>
  <body style="margin:0; background:#f2f4f3; font-family:'Segoe UI', Tahoma, Arial, sans-serif;">
    <div style="max-width:560px;margin:0 auto;padding:24px;">
      <div style="background:#1f4d49;color:#fff;padding:20px 24px;border-radius:16px 16px 0 0;">
        <div style="display:flex;align-items:center;gap:12px;">
          <img src="https://upload.wikimedia.org/wikipedia/ar/d/d7/Saudi_Ministry_of_Defense_Logo.svg" alt="وزارة الدفاع" width="40" height="40" style="display:block;background:#fff;border-radius:8px;padding:4px;" />
          <div>
            <div style="font-size:18px;font-weight:600;letter-spacing:.2px;">ClearanceHub</div>
            <div style="opacity:.85;font-size:13px;margin-top:4px;">التحقق من تسجيل الدخول</div>
          </div>
        </div>
      </div>
      <div style="background:#fff;border-radius:0 0 16px 16px;padding:24px;box-shadow:0 6px 20px rgba(31,77,73,.12);">
        <div style="font-size:18px;color:#111; margin-bottom:8px;">مرحبًا 👋</div>
        <div style="color:#4b5563; font-size:14px; line-height:1.7;">
          رمز التحقق الخاص بك هو:
        </div>
        <div style="margin:16px 0; font-size:28px; letter-spacing:3px; font-weight:700; color:#1f4d49;">
          {otp_code}
        </div>
        <div style="color:#4b5563; font-size:14px;">
          الرمز صالح لمدة <strong style="color:#9b7a2f;">{minutes}</strong> دقائق.
        </div>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;" />
        <div style="color:#6b7280; font-size:12px;">
          إذا لم تطلب هذا الرمز، يمكنك تجاهل الرسالة.
        </div>
      </div>
    </div>
  </body>
</html>
"""
    return subject, text_body, html_body
