# Backend PRD – Card & Access Management System

**Stack:** FastAPI · SQL Server · REST API

---

## 1. Purpose
This document defines the **backend product requirements** for the Card Issuance & Access Permit system. It is intended as a **single source of truth** for backend developers.

The backend is responsible for:
- Handling card and access requests
- Enforcing approval workflows
- Role‑based access control (RBAC)
- Audit logging
- Data export (Excel)

---

## 2. User Roles

| Role Code | Description |
|---------|------------|
| REQUESTER | Request submitter (no login) |
| MANAGER | Requester manager |
| SECURITY | Security department |
| CARD_PRINTING | Card printing & issuance department (execution only) |
| SYSTEM_ADMIN | System administrator |

---

## 3. Request Status Machine

```text
DRAFT
PENDING_MANAGER_APPROVAL
REJECTED_BY_MANAGER
PENDING_SECURITY_APPROVAL
REJECTED_BY_SECURITY
IN_PROCESS
COMPLETED
CANCELLED
```

Rules:
- Status transitions must be validated in service layer
- Rejection requires a reason
- Completed requests are read‑only

---

## 4. Business Rules

1. **Employee master data already exists** in `employees`. When creating any request, the client submits **employee_id only** for employee identity; the backend must **resolve and use stored employee data** (name, department, job title, nationality, etc.) from `employees`.
2. Request creation collects **only request-specific fields** (e.g., card request type/reason, permit areas/reason). No duplicate entry of employee profile fields.
3. **Multiple managers per department are allowed.** Any user with role `DEPT_MANAGER` can see and act on requests for their department.
4. **Managers may submit requests on behalf of their employees** (for frontend UX). This does not change workflow; it only affects who initiated the request.
5. No step can be skipped. Workflow: Manager → Security → Card Printing.
6. Rejection must include a reason.
7. Requests become read-only after reaching final state (printed).
8. RBAC enforced on all endpoints.
9. All state changes must be logged in `audit_logs`.

---

## 5. Database Schema (SQL Server) — Based on OPML

> هذا القسم مطابق لبنية قاعدة البيانات المذكورة في ملف الـ OPML الذي زوّدتني به. الإضافات الوحيدة عليه: **OTP + Tokens**.

### 5.1 employees (الموظفين)

```sql
CREATE TABLE employees (
  med_id BIGINT PRIMARY KEY AUTO_INCREMENT,              -- مخفي للربط مع النظام الأساسي
  employee_id VARCHAR(50) UNIQUE NOT NULL,               -- الرقم الوظيفي
  name_ar VARCHAR(150) NOT NULL,                         -- اسم الموظف عربي
  name_en VARCHAR(150) NOT NULL,                         -- اسم الموظف انجليزي
  job_title VARCHAR(120) NOT NULL,                       -- المسمى الوظيفي
  nationality_ar VARCHAR(120) NOT NULL,                  -- الجنسية عربي
  nationality_en VARCHAR(120) NOT NULL,                  -- الجنسية انجليزي
  department_id INT NOT NULL,                            -- رقم القسم
  department_name VARCHAR(150) NOT NULL,                 -- اسم القسم
  account_status ENUM('ACTIVE','SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_department ON employees(department_id);
CREATE INDEX idx_employees_status ON employees(account_status);
```

---

### 5.2 roles (جدول الصلاحيات)

```sql
CREATE TABLE roles (
  id INT PRIMARY KEY AUTO_INCREMENT,
  role_code VARCHAR(50) UNIQUE NOT NULL,
  role_name VARCHAR(150) NOT NULL
);

-- Examples (seed):
-- DEPT_MANAGER, SECURITY_OFFICER, CARD_PRINTING, ADMIN
```

---

### 5.3 employee_permissions (موظفين الصلاحيات)

> ربط رقم الموظف بالبريد الداخلي والصلاحية

```sql
CREATE TABLE employee_permissions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  employee_id VARCHAR(50) NOT NULL,
  internal_email VARCHAR(150) NOT NULL,
  role_id INT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_permissions_employee (employee_id),
  UNIQUE KEY uq_permissions_email (internal_email),
  FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE INDEX idx_emp_perm_role ON employee_permissions(role_id);
```

---

### 5.4 areas (المناطق)

```sql
CREATE TABLE areas (
  area_id INT PRIMARY KEY AUTO_INCREMENT,               -- رقم المنطقة (ترقيم تلقائي)
  area_name VARCHAR(150) NOT NULL,                      -- اسم المنطقة
  status ENUM('ACTIVE','INACTIVE') NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_areas_status ON areas(status);
```

---

### 5.5 card_requests (طلبات البطاقات)

> مطابق لمستند OPML + إضافة واحدة: `submitted_by_employee_id` لتسجيل "إنشاء الطلب بالنيابة".

```sql
CREATE TABLE card_requests (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  employee_id VARCHAR(50) NOT NULL,                     -- رقم الموظف (صاحب الطلب)
  submitted_by_employee_id VARCHAR(50) NULL,            -- من أنشأ الطلب (قد يكون المدير)
  request_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  request_type ENUM('NEW','RENEW','REPLACE_LOST') NOT NULL,  -- نوع الطلب
  request_reason TEXT,                                  -- سبب الطلب

  manager_employee_id VARCHAR(50),
  manager_updated_at TIMESTAMP NULL,

  security_employee_id VARCHAR(50),
  security_updated_at TIMESTAMP NULL,

  printing_employee_id VARCHAR(50),
  printing_updated_at TIMESTAMP NULL,

  rejection_reason TEXT,
  status ENUM(
    'SUBMITTED_BY_EMPLOYEE',
    'APPROVED_BY_MANAGER',
    'REJECTED_BY_MANAGER',
    'APPROVED_BY_SECURITY',
    'REJECTED_BY_SECURITY',
    'PRINTED_BY_CARD_PRINTING'
  ) NOT NULL DEFAULT 'SUBMITTED_BY_EMPLOYEE',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
  FOREIGN KEY (submitted_by_employee_id) REFERENCES employees(employee_id)
);

CREATE INDEX idx_card_req_status ON card_requests(status);
CREATE INDEX idx_card_req_employee ON card_requests(employee_id);
CREATE INDEX idx_card_req_submitted_by ON card_requests(submitted_by_employee_id);
CREATE INDEX idx_card_req_dates ON card_requests(request_date);
```

---

### 5.6 permit_requests (طلبات التصاريح)

> مطابق لمستند OPML + إضافة واحدة: `submitted_by_employee_id` لتسجيل "إنشاء الطلب بالنيابة".

```sql
CREATE TABLE permit_requests (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  employee_id VARCHAR(50) NOT NULL,                     -- رقم الموظف (صاحب الطلب)
  submitted_by_employee_id VARCHAR(50) NULL,            -- من أنشأ الطلب (قد يكون المدير)
  request_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  request_reason TEXT,

  manager_employee_id VARCHAR(50),
  manager_updated_at TIMESTAMP NULL,

  security_employee_id VARCHAR(50),
  security_updated_at TIMESTAMP NULL,

  printing_employee_id VARCHAR(50),
  printing_updated_at TIMESTAMP NULL,

  rejection_reason TEXT,
  status ENUM(
    'SUBMITTED_BY_EMPLOYEE',
    'APPROVED_BY_MANAGER',
    'REJECTED_BY_MANAGER',
    'APPROVED_BY_SECURITY',
    'REJECTED_BY_SECURITY',
    'PRINTED_BY_CARD_PRINTING'
  ) NOT NULL DEFAULT 'SUBMITTED_BY_EMPLOYEE',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
  FOREIGN KEY (submitted_by_employee_id) REFERENCES employees(employee_id)
);

CREATE INDEX idx_permit_req_status ON permit_requests(status);
CREATE INDEX idx_permit_req_employee ON permit_requests(employee_id);
CREATE INDEX idx_permit_req_submitted_by ON permit_requests(submitted_by_employee_id);
CREATE INDEX idx_permit_req_dates ON permit_requests(request_date);
```

---

### 5.7 permit_request_areas (ربط التصاريح بالمناطق)

> لأن الطلب يسمح بأكثر من منطقة (many-to-many)

```sql
CREATE TABLE permit_request_areas (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  permit_request_id BIGINT NOT NULL,
  area_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_permit_area (permit_request_id, area_id),
  FOREIGN KEY (permit_request_id) REFERENCES permit_requests(id) ON DELETE CASCADE,
  FOREIGN KEY (area_id) REFERENCES areas(area_id)
);
```

---

### 5.8 user_otp (OTP)

> إضافة مطلوبة (ناقصه في OPML): لتسجيل دخول المدير/الأمن/الطباعة/الادمن عبر البريد + OTP

```sql
CREATE TABLE user_otp (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  internal_email VARCHAR(150) NOT NULL,
  otp_code VARCHAR(10) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  is_used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_otp_email (internal_email),
  INDEX idx_user_otp_expires (expires_at)
);
```

---

### 5.9 auth_tokens (Tokens)

> إضافة مطلوبة (ناقصه في OPML): تخزين refresh tokens بشكل hash

```sql
CREATE TABLE auth_tokens (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  internal_email VARCHAR(150) NOT NULL,
  token_hash VARCHAR(255) NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_auth_tokens_email (internal_email),
  INDEX idx_auth_tokens_expires (expires_at),
  INDEX idx_auth_tokens_revoked (revoked)
);
```

---

### 5.10 audit_logs (Audit)

```sql
CREATE TABLE audit_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  entity_type VARCHAR(50) NOT NULL,
  entity_id BIGINT NOT NULL,
  action VARCHAR(100) NOT NULL,
  performed_by_email VARCHAR(150),
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_audit_entity (entity_type, entity_id),
  INDEX idx_audit_created (created_at)
);
```

---

## 6. API Responsibilities (FULL SPEC)

> All endpoints are mandatory. No hidden behavior allowed.

---

### 6.1 Authentication

#### Request OTP
```
POST /auth/request-otp
```
Body:
```json
{ "email": "manager@company.com" }
```

---

#### Verify OTP
```
POST /auth/verify-otp
```
Body:
```json
{ "email": "manager@company.com", "otp": "123456" }
```

Response:
```json
{ "access_token": "jwt", "refresh_token": "jwt" }
```

---

### 6.2 Create Card Request

```
POST /requests/card
```

Body (employee profile is resolved from DB):
```json
{
  "employee_id": "EMP123",
  "request_type": "NEW",
  "request_reason": "New joiner",
  "photo_url": "https://..."
}
```

Auth behavior:
- **No Authorization header**: employee self-submission.
- **With Authorization**:
  - role=`DEPT_MANAGER`: can submit on behalf **only for employees in the same department**.
  - role=`ADMIN`: can submit on behalf for any employee.

Backend behavior:
- Validate employee exists in `employees`.
- Insert into `card_requests`:
  - `employee_id` = target employee
  - `submitted_by_employee_id` = authenticated creator employee_id (if any)
  - `status` = `SUBMITTED_BY_EMPLOYEE`
- Write audit log entry.

Creates:
- requests (status=PENDING_MANAGER_APPROVAL)
- card_requests
- audit log

---

### 6.3 Create Permit (Access) Request

```
POST /requests/access
```

Body (employee profile is resolved from DB):
```json
{
  "employee_id": "EMP123",
  "area_ids": [1, 3, 7],
  "request_reason": "Maintenance work"
}
```

Auth behavior:
- **No Authorization header**: employee self-submission.
- **With Authorization**:
  - role=`DEPT_MANAGER`: can submit on behalf **only for employees in the same department**.
  - role=`ADMIN`: can submit on behalf for any employee.

Backend behavior:
- Validate employee exists in `employees`.
- Validate areas exist and are ACTIVE in `areas`.
- Insert into `permit_requests` (status=`SUBMITTED_BY_EMPLOYEE`).
- Insert N rows into `permit_request_areas` for `area_ids`.
- Write audit log entry.

---

### 6.4 Get Request Details

```
GET /requests/{id}
```

Returns full request details including employee snapshot, approvals, and current status.

---

### 6.5 Get Employee (Read-Only)

> Frontend helper endpoint. **Read-only**. No sensitive fields.

```
GET /employees/{employee_id}
```

Auth behavior:
- No authentication required for basic lookup (can be rate-limited).
- Optional Authorization allowed.

Response:
```json
{
  "employee_id": "EMP123",
  "name_ar": "أحمد علي",
  "name_en": "Ahmed Ali",
  "job_title": "Engineer",
  "department_id": 10,
  "department_name": "IT",
  "account_status": "ACTIVE"
}
```

Backend behavior:
- Fetch from `employees`.
- Return 404 if not found or account_status != ACTIVE.

---

### 6.6 List Areas

> Used by Access Request UI.

```
GET /areas
```

Query params (optional):
- `status=ACTIVE`

Response:
```json
[
  {
    "area_id": 1,
    "area_name": "Server Room"
  },
  {
    "area_id": 2,
    "area_name": "Data Center"
  }
]
```

Backend behavior:
- Return only ACTIVE areas by default.
- Sorted by area_name.

---

### 6.7 List Requests

```
GET /requests/{id}
```

Returns:
- request
- specific payload
- approvals timeline

---

### 6.5 List Requests

```
GET /requests?type=&status=&from=&to=
```

---

### 6.6 Approve Request

```
POST /requests/{id}/approve
```

Rules:
- Manager → PENDING_SECURITY_APPROVAL
- Security → IN_PROCESS

---

### 6.7 Reject Request

```
POST /requests/{id}/reject
```

Body:
```json
{ "reason": "Invalid data" }
```

---

### 6.8 Complete Request

```
POST /requests/{id}/complete
```

Only CARD_PRINTING allowed.

---

### 6.9 Export Excel

```
GET /reports/requests/excel
```

---

## 7. Backend Architecture

```text
app/
 ├─ main.py
 ├─ api/
 │   ├─ auth.py
 │   ├─ requests.py
 │   ├─ approvals.py
 │   └─ reports.py
 ├─ services/
 │   ├─ request_service.py
 │   ├─ approval_service.py
 │   ├─ auth_service.py
 ├─ models/
 │   ├─ user.py
 │   ├─ request.py
 │   ├─ approval.py
 │   └─ audit.py
 ├─ schemas/
 │   ├─ request.py
 │   ├─ approval.py
 │   └─ auth.py
 └─ utils/
     ├─ otp.py
     ├─ excel.py
     └─ audit.py
```

---

## 8. Acceptance Criteria

- Workflow enforcement validated
- Rejection requires reason
- Full audit logging
- RBAC on all endpoints
- Excel export works without frontend

---

## 9. Backend Deliverables

- REST APIs
- SQL migrations
- Postman collection
- README.md

---

**End of Document**
