from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common.database import get_db
from departments.departments_db import Department
from departments.roles_db import Role, Permission, RolePermission

router = APIRouter(tags=["roles"], prefix="/departments/{department_id}/roles")


class NameModel(BaseModel):
    name: str

    class Config:
        from_attributes = True


class ListModel(NameModel):
    id: int


class CreateModel(BaseModel):
    name: str
    permissions: list[str] | None = None

    class Config:
        from_attributes = True


class UpdateModel(CreateModel):
    name: str | None = None


class FullModel(ListModel):
    permissions: list[ListModel]


@router.get("/", response_model=list[ListModel])
def get_roles(department_id: int, db: Session = Depends(get_db)):
    if Department.find_by_id(db, department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return Role.get_list(db, department_id=department_id)


@router.post("/", response_model=FullModel)
def create_role(department_id: int, create_data: CreateModel, db: Session = Depends(get_db)) -> Role:
    if Department.find_by_id(db, department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    new_role: Role = Role.get_or_create(db, name=create_data.name, department_id=department_id)
    if create_data.permissions is not None:
        new_permissions: list[int] = [
            Permission.get_or_create(db, name=permission).id for permission in set(create_data.permissions)
        ]
        RolePermission.create_bulk(db, new_role.id, new_permissions)
    return new_role


@router.get("/{role_id}/", response_model=FullModel)
def get_role(department_id: int, role_id: int, db: Session = Depends(get_db)) -> Role:
    if Department.find_by_id(db, department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    role: Role = Role.find_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/{role_id}/", response_model=FullModel)
def update_role(department_id: int, role_id: int, update_data: UpdateModel, db: Session = Depends(get_db)) -> Role:
    if Department.find_by_id(db, department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    role: Role = Role.find_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    update_data: dict[str, Any] = update_data.model_dump(exclude_none=True)
    for key, value in update_data.items():
        if key != "permissions":
            setattr(role, key, value)
            continue
        received_permissions: set[int] = {
            Permission.get_or_create(db, name=permission).id for permission in value
        }
        permissions_from_db: set[int] = {permission.id for permission in role.permissions}
        RolePermission.update_permissions(db, role.id, received_permissions, permissions_from_db)
    return role


@router.delete("/{role_id}/")
def delete_role(department_id: int, role_id: int, db: Session = Depends(get_db)) -> None:
    if Department.find_by_id(db, department_id) is None:
        raise HTTPException(status_code=404, detail="Department not found")
    role: Role = Role.find_by_id(db, role_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    role.delete(db)
