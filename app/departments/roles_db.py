from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, Query

from common.abstracts import BaseModel
from common.database import Base
from departments.employees_db import EmployeeRole


class Permission(BaseModel):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    @classmethod
    def create_bulk(cls, db: Session, role_id: int, permissions: list[int]) -> None:
        db.add_all(
            cls(role_id=role_id, permission_id=permission) for permission in permissions
        )
        db.commit()

    @classmethod
    def delete_by_ids(cls, db: Session, role_id: int, permissions: set[int]) -> None:
        stmt: Query = db.query(cls).filter(
            cls.role_id == role_id,
            cls.permission_id.in_(permissions),
        )
        stmt.delete()
        db.commit()

    @classmethod
    def update_permissions(
            cls,
            db: Session,
            role_id: int,
            new_data: set[int],
            db_data: set[int],
    ) -> None:
        cls.delete_by_ids(db, role_id, db_data - new_data)
        cls.create_bulk(db, role_id, list(new_data - db_data))


class Role(BaseModel):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="CASCADE"),
    )

    permissions = relationship("Permission", secondary=RolePermission.__table__)

    employees = relationship("Employee", secondary=EmployeeRole.__table__, back_populates="roles")
