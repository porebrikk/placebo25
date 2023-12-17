from typing import Any, Callable

from pytest import fixture
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from departments.departments_db import Department
from departments.employees_db import Employee
from departments.roles_db import Role
from main import app
from common.abstracts import BaseModel
from common.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def delete_by_id(session: Session, entry_id: int, table: type[BaseModel]) -> None:
    row = table.find_by_id(session, entry_id)
    row.delete(session)
    session.commit()
    assert table.find_by_id(session, entry_id) is None


@fixture
def test_department_data() -> dict[str, Any]:
    return {"name": "test_name", "parent_id": None}


@fixture
def department_maker(
        session: Session,
        test_department_data: dict[str, Any],
) -> Callable[[], Department]:
    created: list[int] = []

    def department_maker_inner() -> Department:
        department: Department = Department.create(session, **test_department_data)
        created.append(department.id)
        return department

    yield department_maker_inner

    for department_id in created:
        delete_by_id(session, department_id, Department)


@fixture
def test_department(department_maker: Callable[[], Department]) -> int:
    department: Department = department_maker()
    return department.id


@fixture
def test_employee_data() -> dict[str, Any]:
    return {"name": "John", "surname": "Doe", "department_id": None}


@fixture
def employee_maker(
        session: Session,
        test_employee_data: dict[str, Any],
) -> Callable[[], Employee]:
    created: list[int] = []

    def employee_maker_inner() -> Employee:
        employee: Employee = Employee.create(session, **test_employee_data)
        created.append(employee.id)
        return employee

    yield employee_maker_inner

    for employee_id in created:
        delete_by_id(session, employee_id, Employee)


@fixture
def test_employee(employee_maker: Callable[[], Employee]) -> int:
    employee: Employee = employee_maker()
    return employee.id


@fixture
def test_role_data(test_department) -> dict[str, Any]:
    return {"name": "test_role", "department_id": test_department}


@fixture
def role_maker(
        session: Session,
        test_role_data: dict[str, Any],
) -> Callable[[], Employee]:
    created: list[int] = []

    def role_maker_inner() -> Employee:
        role: Role = Role.get_or_create(session, **test_role_data)
        created.append(role.id)
        return role

    yield role_maker_inner

    for role_id in created:
        delete_by_id(session, role_id, Role)


@fixture
def test_role(session: Session, test_role_data: dict[str, Any]) -> int:
    role: Role = Role.get_or_create(session, **test_role_data)

    assert Role.find_by_id(session, role.id) is not None

    yield role.id

    role.delete(session)
