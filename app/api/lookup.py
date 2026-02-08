from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.database import get_db
from app.models.area import Area
from app.models.employee import Employee
from app.schemas.area import AreaRead
from app.schemas.employee import EmployeeRead
from app.services.employee_import_service import import_employees_from_csv

router = APIRouter(tags=["lookup"])

ADMIN_ROLES = {"ADMIN", "SYSTEM_ADMIN"}


@router.post("/employees/import")
def import_employees_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(require_roles(ADMIN_ROLES)),
):
    return import_employees_from_csv(db, file)


@router.get("/employees/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: str, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee or employee.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return employee


@router.get("/areas", response_model=list[AreaRead])
def list_areas(
    status: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Area)
    if status:
        query = query.filter(Area.status == status.upper())
    else:
        query = query.filter(Area.status == "ACTIVE")
    return query.order_by(Area.area_name).all()
