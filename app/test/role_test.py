from typing import Any

from fastapi.testclient import TestClient
from pytest import mark, param
from werkzeug.test import Response

TEST_DATA = {"id": 1, "name": "test_role", "permissions": [{"id": 1, "name": "coffee_machine"}]}


@mark.parametrize(
    ("name", "permissions", "code", "expected_data"),
    [param(TEST_DATA["name"], [TEST_DATA["permissions"][-1]["name"]], 200, TEST_DATA)],
)
def test_crd_role(
        client: TestClient,
        test_department: int,
        name: str,
        permissions: list[str],
        code: int,
        expected_data: dict[str, Any],
):
    result: Response = client.post(
        f"/departments/{test_department}/roles/", json={"name": name, "permissions": permissions}
    )

    assert result.status_code == code
    assert result.json() == expected_data

    roles_list: Response = client.get(f"/departments/{test_department}/roles/")
    assert roles_list.status_code == code
    assert len(roles_list.json()) != 0

    deleting: Response = client.delete(f"/departments/{test_department}/roles/{expected_data.get('id')}/")
    assert deleting.status_code == code
    assert len(client.get(f"/departments/{test_department}/roles/").json()) == 0


@mark.parametrize(
    ("name", "permissions", "code", "expected_data"),
    [
        param(
            "new_name",
            [TEST_DATA["permissions"][-1]["name"]],
            200,
            dict(id=TEST_DATA["id"], name="new_name", permissions=TEST_DATA["permissions"])
        )
    ],
)
def test_update_role(
        client: TestClient,
        test_department: int,
        test_role: int,
        name: str,
        permissions: list[str],
        code: int,
        expected_data: dict[str, Any],
):
    first_result: Response = client.patch(
        f"/departments/{test_department}/roles/{test_role}/",
        json={"name": name, "permissions": permissions},
    )

    assert first_result.status_code == code
    assert first_result.json() == expected_data

    new_permissions: list[str] = ["toilet", "hall"]
    new_expected: dict[str, Any] = dict(
        name=expected_data["name"],
        id=expected_data["id"],
        permissions=[{"id": num, "name": name} for num, name in enumerate(new_permissions, 2)],
    )

    second_result: Response = client.patch(
        f"/departments/{test_department}/roles/{test_role}/",
        json={"permissions": new_permissions},
    )

    assert second_result.status_code == code
    assert second_result.json() == new_expected


@mark.parametrize(
    ("department_id", "role_id", "table"),
    [
        param(99, 1, "Department"),
        param(1, 99, "Role"),
    ]
)
def test_not_found_exceptions(
        client: TestClient,
        test_department: int,
        test_role: int,
        department_id: int,
        role_id: int,
        table: str,
):
    post_data: dict[str, Any] = TEST_DATA.copy()
    post_data.pop("permissions")
    exceptions: list[Response] = list()

    exceptions.append(client.get(f"/departments/{department_id}/roles/{role_id}/"))
    exceptions.append(client.patch(f"/departments/{department_id}/roles/{role_id}/", json=post_data))
    exceptions.append(client.delete(f"/departments/{department_id}/roles/{role_id}/"))
    if table == "Department":
        exceptions.append(client.get(f"/departments/{department_id}/roles/"))
        exceptions.append(client.post(f"/departments/{department_id}/roles/", json=post_data))

    for exception in exceptions:
        assert exception.status_code == 404
        assert exception.json() == {"detail": f"{table} not found"}


@mark.parametrize(
    ("name", "code", "expected_data"),
    [
        param("test_permission", 200, {"id": 1, "name": "test_permission"}),
    ]
)
def test_permissions(
        client: TestClient,
        name: str,
        code: int,
        expected_data: dict[str, Any],
):
    result: Response = client.post("/permissions/", json={"name": name})
    assert result.status_code == code
    assert result.json() == expected_data

    permission_list: Response = client.get("/permissions/")
    assert permission_list.status_code == code
    assert len(permission_list.json()) != 0

    assert client.delete(f"/permissions/{99}/").json() == {"detail": "Permission not found"}

    deleting: Response = client.delete(f"/permissions/{expected_data.get('id')}/")
    assert deleting.status_code == code
    assert len(client.get("/permissions/").json()) == 0
