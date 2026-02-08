# ClearanceHub Backend

FastAPI backend for Card Issuance & Access Permit system.

## Stack
- FastAPI
- MySQL
- SQLAlchemy + Alembic
- JWT auth

## Setup
1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy environment file and edit values:

```bash
copy .env.example .env
```

3. Run migrations:

```bash
alembic upgrade head
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```


## Authentication (OTP)
- OTP is **fixed** for testing: `123456` (set in `.env`).
- Use `/auth/request-otp` then `/auth/verify-otp`.

## SMTP (OTP Email)
Configure SMTP settings in `.env` to send OTP emails:
```
SMTP_ENABLED=true
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-user
SMTP_PASSWORD=your-pass
SMTP_FROM_EMAIL=no-reply@company.com
SMTP_FROM_NAME=ClearanceHub
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_TIMEOUT_SECONDS=10
```

## Key Endpoints
- `POST /requests/card`
- `POST /requests/access`
- `GET /requests/{id}`
- `GET /requests?type=&status=&from=&to=`
- `POST /requests/{id}/approve`
- `POST /requests/{id}/reject`
- `POST /requests/{id}/complete`
- `GET /reports/requests/excel`

## Project Structure
```
app/
  main.py
  api/
  services/
  models/
  schemas/
  utils/
  db/
```

## Notes
- Requesters do not authenticate.
- RBAC enforced on staff endpoints.
- All state changes are audited.
