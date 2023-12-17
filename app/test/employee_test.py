from typing import Any

from fastapi.testclient import TestClient
from pytest import mark, param
from pytest_lazyfixture import lazy_fixture
from werkzeug.test import Response


@mark.parametrize(
    ("name", "surname", "department_id", "roles", "code", "expected_data"),
    [
        param("John", "Doe", None, None, 200, lazy_fixture("test_employee_data")),
        param(
            "Thomas",
            "Shelby",
            lazy_fixture("test_department"),
            [{"name": "test_role"}],
            200,
            {"name": "Thomas", "surname": "Shelby", "department_id": 1},
        ),
        param("Steve", "Jobs", 99, None, 404, {"detail": "Department not found"}),
    ],
)
def test_crd_employee(
        client: TestClient,
        test_department: int,
        name: str,
        surname: str,
        department_id: int | None,
        roles: list[dict[str, str]] | None,
        code: int,
        expected_data: dict[str, Any]
):
    result: Response = client.post(
        "/employees/",
        json={"name": name, "surname": surname, "department_id": department_id, "roles": roles}
    )
    expected_data: dict[str, Any] = (dict(id=1, roles=roles or [], **expected_data) if code == 200 else expected_data)

    assert result.status_code == code
    assert result.json() == expected_data

    if code != 404:
        employee_list: Response = client.get("/employees/")
        assert employee_list.status_code
        assert len(employee_list.json()) != 0

        if (result_dep := result.json().get("department_id")) is not None:
            assert (department := client.get(f"/departments/{result_dep}")).status_code == code
            assert len(department.json().get("employees")) != 0

            assert (roles_list := client.get(f"/departments/{result_dep}/roles/")).status_code == code
            assert len(roles_list.json()) != 0

        deleting: Response = client.delete(f"/employees/{expected_data.get('id')}")
        assert deleting.status_code == code
        assert len(client.get("/employees/").json()) == 0


@mark.parametrize(
    ("name", "surname", "department_id", "role", "code", "expected_data"),
    [
        param(None, None, None, None, 200, lazy_fixture("test_employee_data")),
        param(
            "new_name",
            "new_surname",
            1,
            lazy_fixture("test_role_data"),
            200,
            {"name": "new_name", "surname": "new_surname", "department_id": 1},
        ),
    ],
)
def test_update_employee(
        client: TestClient,
        test_employee: int,
        test_department: int,
        test_role: int,
        name: str | None,
        surname: str | None,
        department_id: int | None,
        role: dict[str, Any] | None,
        code: int,
        expected_data: dict[str, Any],
):
    roles: list[dict[str, Any]] = [] if role is None else [role]
    result: Response = client.patch(
        f"/employees/{test_employee}/",
        json={"name": name, "surname": surname, "department_id": department_id, "roles": roles},
    )
    roles = [dict(name=role["name"], id=1)] if len(roles) >= 1 else []
    expected_data: dict[str, Any] = dict(id=1, roles=roles, **expected_data)

    assert result.status_code == code
    assert result.json() == expected_data
