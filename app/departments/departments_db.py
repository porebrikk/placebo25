from typing import Self

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from common.abstracts import BaseModel


class Department(BaseModel):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
    )
    parent = relationship(
        "Department",
        remote_side=[id],
        foreign_keys=[parent_id],
        back_populates="children",
        passive_deletes=True,
    )

    children = relationship("Department", passive_deletes=True, back_populates="parent")
    employees = relationship("Employee", passive_deletes=True)

    @classmethod
    def create(cls, db: Session, name: str, parent_id: int | None) -> Self:
        new_department: Self = cls(name=name, parent_id=parent_id)
        db.add(new_department)
        db.commit()
        return new_department
