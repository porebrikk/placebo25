from typing import Any, Callable

from fastapi.testclient import TestClient
from pytest import mark, param
from pytest_lazyfixture import lazy_fixture
from werkzeug.test import Response

from departments.departments_db import Department


@mark.parametrize(
    ("data", "code"),
    [param(lazy_fixture("test_department_data"), 200)],
)
def test_crd_department(
        client: TestClient,
        data: dict[str, int | None],
        code: int,
):
    result: Response = client.post("/departments/", json=data)
    response: dict[str, Any] = dict(id=1, **data)

    assert result.status_code == code
    assert result.json() == response

    department_list: Response = client.get("/departments/")
    assert department_list.status_code == code
    assert len(department_list.json()) != 0

    deleting: Response = client.delete(f"/departments/{response.get('id')}/")
    assert deleting.status_code == code
    assert len(client.get("/departments/").json()) == 0


@mark.parametrize(
    ("name", "parent_id", "code", "expected_data"),
    [
        param(None, None, 200, lazy_fixture("test_department_data")),
        param("new_name", 1, 200, {"name": "new_name", "parent_id": 1}),
        param("something", 11, 404, {"detail": "Department not found"}),

    ]
)
def test_update_department(
        client: TestClient,
        department_maker: Callable[[], Department],
        name: str | None,
        parent_id: int | None,
        code: int,
        expected_data: dict[str, Any]
):
    first_dep: int = department_maker().id
    second_dep: int = department_maker().id

    expected_data: dict[str, Any] = (
        dict(id=second_dep, children=[], employees=[], **expected_data) if code == 200 else expected_data
    )

    updated_dep: Response = client.patch(
        f"/departments/{second_dep}/", json={"name": name, "parent_id": parent_id}
    )
    assert updated_dep.status_code == code
    assert updated_dep.json() == expected_data

    if parent_id == 1:
        parent_response: Response = client.get(f"/departments/{first_dep}/")
        assert parent_response.status_code == code
        assert len(parent_response.json().get("children")) != 0
        assert parent_response.json().get("children")[-1] == {"id": second_dep, "name": name}
