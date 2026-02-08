import csv
from io import StringIO

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.employee import Employee

REQUIRED_HEADERS = {
    "MedID",
    "EmpNameAR",
    "EmpNameEN",
    "CountryNameEN",
    "CountryNameAR",
    "DepID",
    "DepartmentName",
    "EmpID",
    "EmpStatusName",
    "JobTitleNameSum",
}

HEADER_MAP = {
    "MedID": "med_id",
    "EmpID": "employee_id",
    "EmpNameAR": "name_ar",
    "EmpNameEN": "name_en",
    "JobTitleNameSum": "job_title",
    "CountryNameAR": "nationality_ar",
    "CountryNameEN": "nationality_en",
    "DepID": "department_id",
    "DepartmentName": "department_name",
    "EmpStatusName": "account_status",
}


def _normalize_header(value: str) -> str:
    return value.strip().lstrip("﻿")


def _parse_int(value: str, field: str, row_number: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Row {row_number}: invalid {field}",
        )


def _map_status(value: str) -> str:
    normalized = (value or "").strip()
    return "ACTIVE" if normalized == "على رأس العمل" else "SUSPENDED"


def import_employees_from_csv(db: Session, file: UploadFile) -> dict:
    if not file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file required")

    content = file.file.read()
    try:
        text_content = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid CSV encoding") from exc

    reader = csv.DictReader(StringIO(text_content))
    if not reader.fieldnames:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV headers missing")

    header_lookup = {_normalize_header(name): name for name in reader.fieldnames}
    missing = [name for name in REQUIRED_HEADERS if name not in header_lookup]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing columns: {', '.join(sorted(missing))}",
        )

    rows = []
    seen_med_ids = set()
    seen_employee_ids = set()

    for row_number, row in enumerate(reader, start=2):
        med_id_value = row.get(header_lookup["MedID"], "").strip()
        emp_id_value = row.get(header_lookup["EmpID"], "").strip()

        if not med_id_value or not emp_id_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_number}: MedID and EmpID are required",
            )

        med_id = _parse_int(med_id_value, "MedID", row_number)
        department_id = _parse_int(
            row.get(header_lookup["DepID"], "").strip(),
            "DepID",
            row_number,
        )

        if med_id in seen_med_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_number}: duplicate MedID",
            )
        if emp_id_value in seen_employee_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Row {row_number}: duplicate EmpID",
            )

        seen_med_ids.add(med_id)
        seen_employee_ids.add(emp_id_value)

        rows.append(
            {
                "med_id": med_id,
                "employee_id": emp_id_value,
                "name_ar": row.get(header_lookup["EmpNameAR"], "").strip(),
                "name_en": row.get(header_lookup["EmpNameEN"], "").strip(),
                "job_title": row.get(header_lookup["JobTitleNameSum"], "").strip(),
                "nationality_ar": row.get(header_lookup["CountryNameAR"], "").strip(),
                "nationality_en": row.get(header_lookup["CountryNameEN"], "").strip(),
                "department_id": department_id,
                "department_name": row.get(header_lookup["DepartmentName"], "").strip(),
                "account_status": _map_status(row.get(header_lookup["EmpStatusName"], "")),
            }
        )

    engine = db.get_bind()
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        Employee.__table__.drop(bind=conn, checkfirst=True)
        Employee.__table__.create(bind=conn)
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        if rows:
            conn.execute(Employee.__table__.insert(), rows)

    return {"imported": len(rows)}
