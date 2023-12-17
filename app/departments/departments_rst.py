from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common.database import get_db
from departments.departments_db import Department

from departments.employees_rst import IndexModel as EmployeeModel


router = APIRouter(tags=["departments"], prefix="/departments")


class ListModel(BaseModel):
    id: int
    name: str


class CreateModel(BaseModel):
    name: str
    parent_id: int | None = None

    class Config:
        from_attributes = True


class PreviewModel(CreateModel):
    id: int


class UpdateModel(CreateModel):
    name: str | None = None


class FullModel(PreviewModel):
    children: list[ListModel]
    employees: list[EmployeeModel]


@router.get("/", response_model=list[ListModel])
def get_departments(db: Session = Depends(get_db)) -> list[Department]:
    return Department.get_list(db)


@router.post("/", response_model=PreviewModel)
def create_department(department_data: CreateModel, db: Session = Depends(get_db)) -> Department:
    return Department.create(db, department_data.name, department_data.parent_id)


@router.get("/{department_id}/", response_model=FullModel)
def get_department(department_id: int, db: Session = Depends(get_db)) -> Department:
    department: Department = Department.find_by_id(db, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


@router.patch("/{department_id}/", response_model=FullModel)
def update_department(department_id: int, update_data: UpdateModel, db: Session = Depends(get_db)) -> Department:
    department: Department = Department.find_by_id(db, department_id)
    parent: Department = Department.find_by_id(db, update_data.parent_id)
    if parent is None and update_data.parent_id is not None or department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    department.parent_id = update_data.parent_id if parent not in department.children else department.parent_id
    department.name = update_data.name or department.name
    db.add(department)
    db.commit()
    return department


@router.delete("/{department_id}/")
def delete_department(department_id: int, db: Session = Depends(get_db)) -> None:
    department: Department = Department.find_by_id(db, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    department.delete(db)
