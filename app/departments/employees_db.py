from typing import Self

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, Query

from common.abstracts import BaseModel
from common.database import Base


class EmployeeRole(Base):
    __tablename__ = "employee_roles"

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    @classmethod
    def create_bulk(cls, db: Session, employee_id: int, roles: list[int]) -> None:
        db.add_all(
            cls(employee_id=employee_id, role_id=role) for role in roles
        )
        db.commit()

    @classmethod
    def delete_by_ids(cls, db: Session, employee_id: int, roles: set[int]) -> None:
        stmt: Query = db.query(cls).filter(
            cls.employee_id == employee_id,
            cls.role_id.in_(roles),
        )
        stmt.delete()
        db.commit()

    @classmethod
    def update_roles(
            cls,
            db: Session,
            employee_id: int,
            new_data: set[int],
            db_data: set[int],
    ) -> None:
        cls.delete_by_ids(db, employee_id, db_data - new_data)
        cls.create_bulk(db, employee_id, list(new_data - db_data))


class Employee(BaseModel):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    surname: Mapped[str] = mapped_column(String(20))

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL")
    )

    roles = relationship("Role", secondary=EmployeeRole.__table__, back_populates="employees")

    @classmethod
    def create(cls, db: Session, name: str, surname: str, department_id: int | None) -> Self:
        new_employee: Self = cls(name=name, surname=surname, department_id=department_id)
        db.add(new_employee)
        db.commit()
        return new_employee
