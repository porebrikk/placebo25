from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common.database import get_db
from departments.roles_db import Permission

router = APIRouter(tags=["permissions"], prefix="/permissions")


class CreateModel(BaseModel):
    name: str

    class Config:
        from_attributes = True


class IndexModel(CreateModel):
    id: int


@router.get("/", response_model=list[IndexModel])
def get_permissions(db: Session = Depends(get_db)) -> list[Permission]:
    return Permission.get_list(db)


@router.post("/", response_model=IndexModel)
def create_permission(create_data: CreateModel, db: Session = Depends(get_db)) -> Permission:
    return Permission.get_or_create(db, name=create_data.name)


@router.delete("/{permission_id}/")
def delete_permission(permission_id: int, db: Session = Depends(get_db)) -> None:
    permission: Permission = Permission.find_by_id(db, permission_id)
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    permission.delete(db)
