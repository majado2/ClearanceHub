from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ClearanceHub API"
    environment: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 9022

    # Database
    database_url: str = "mssql+pyodbc://sa:YourPassword@localhost:1433/clearancehub?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14

    # OTP (testing)
    otp_fixed_enabled: bool = True
    otp_fixed_code: str = "123456"
    otp_expire_minutes: int = 10

    # SMTP (OTP email)
    smtp_enabled: bool = False
    smtp_host: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "no-reply@clearancehub.local"
    smtp_from_name: str = "ClearanceHub"
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_timeout_seconds: int = 10

    class Config:
        env_file = ".env"


settings = Settings()
