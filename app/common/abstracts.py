from re import sub
from typing import Self

from sqlalchemy.orm import Session

from common.database import Base


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def get_list(cls, db: Session, **kwargs) -> list[Self]:
        return db.query(cls).filter_by(**kwargs).all()

    @classmethod
    def get_first(cls, db: Session, **kwargs) -> Self:
        return db.query(cls).filter_by(**kwargs).first()

    @classmethod
    def get_or_create(cls, db: Session, **kwargs) -> Self:
        name: str = sub(" _,./\\+=", "-", kwargs.pop("name").lower())
        row: Self = cls.get_first(db, name=name, **kwargs)
        if row is None:
            row: Self = cls(name=name, **kwargs)
            db.add(row)
            db.commit()
        return row

    @classmethod
    def find_by_id(cls, db: Session, entry_id: int) -> Self | None:
        return db.query(cls).filter_by(id=entry_id).first()

    @classmethod
    def find_by_name(cls, db: Session, entry_name: str) -> Self | None:
        return db.query(cls).filter_by(name=entry_name).first()

    def delete(self, db: Session) -> None:
        db.delete(self)
        db.commit()
