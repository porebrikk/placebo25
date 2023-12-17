from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common.database import get_db
from departments.departments_db import Department
from departments.employees_db import Employee, EmployeeRole
from departments.roles_rst import ListModel as ListRoleModel
from departments.roles_rst import NameModel as NameRoleModel
from departments.roles_db import Role

router = APIRouter(tags=["employees"], prefix="/employees")


class IndexModel(BaseModel):
    id: int

    name: str
    surname: str

    class Config:
        from_attributes = True


class CreateModel(BaseModel):
    name: str
    surname: str
    department_id: int | None
    roles: list[NameRoleModel] | None = None


class PreviewModel(CreateModel):
    id: int


class UpdateModel(CreateModel):
    name: str | None
    surname: str | None

    class Config:
        from_attributes = True


class FullModel(PreviewModel):
    roles: list[ListRoleModel]


@router.get("/", response_model=list[IndexModel])
def get_employees(db: Session = Depends(get_db)) -> list[Employee]:
    return Employee.get_list(db)


@router.post("/", response_model=PreviewModel)
def create_employee(create_data: CreateModel, db: Session = Depends(get_db)) -> Employee:
    if create_data.department_id is not None:
        if Department.find_by_id(db, create_data.department_id) is None:
            raise HTTPException(status_code=404, detail="Department not found")

    employee: Employee = Employee.create(db, create_data.name, create_data.surname, create_data.department_id)
    if create_data.department_id is not None and create_data.roles is not None:
        roles_list: list[int] = [
            Role.get_or_create(
                db,
                name=role.model_dump()["name"],
                department_id=create_data.department_id,
            ).id
            for role in create_data.roles
        ]
        EmployeeRole.create_bulk(db, employee.id, roles_list)
    return employee


@router.get("/{employee_id}/", response_model=FullModel)
def get_employee(employee_id: int, db: Session = Depends(get_db)) -> Employee:
    employee: Employee = Employee.find_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.patch("/{employee_id}/", response_model=FullModel)
def update_employee(employee_id: int, update_data: UpdateModel, db: Session = Depends(get_db)) -> Employee:
    employee: Employee = Employee.find_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    update_data: dict[str, Any] = update_data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        if key != "roles":
            setattr(employee, key, value)
            continue
        received_roles: set[int] = {
            Role.get_or_create(db, name=role["name"], department_id=update_data["department_id"]).id
            for role in value
        }
        roles_from_db: set[int] = {role.id for role in employee.roles}
        EmployeeRole.update_roles(db, employee.id, received_roles, roles_from_db)
    return employee


@router.delete("/{employee_id}/")
def delete_employee(employee_id: int, db: Session = Depends(get_db)) -> None:
    employee: Employee = Employee.find_by_id(db, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    employee.delete(db)
