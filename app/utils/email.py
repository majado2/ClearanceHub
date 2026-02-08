import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


def send_email(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> None:
    if not settings.smtp_enabled:
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = to_email
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")

    if settings.smtp_use_ssl:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(
            settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds, context=context
        )
    else:
        server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=settings.smtp_timeout_seconds)

    try:
        if settings.smtp_use_tls and not settings.smtp_use_ssl:
            server.starttls(context=ssl.create_default_context())
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)
    finally:
        server.quit()
