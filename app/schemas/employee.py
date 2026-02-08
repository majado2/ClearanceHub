from pydantic import BaseModel


class EmployeeRead(BaseModel):
    employee_id: str
    name_ar: str
    name_en: str
    job_title: str
    department_id: int
    department_name: str
    account_status: str

    class Config:
        from_attributes = True


class EmployeeSnapshot(EmployeeRead):
    nationality_ar: str
    nationality_en: str

    class Config:
        from_attributes = True
