def test_get_tasks_requires_auth(client):
    response = client.get("/tasks/")
    assert response.status_code == 401


def test_task_crud_and_audit_log(client, auth_headers):
    created = client.post(
        "/tasks/",
        json={"title": "Production readiness", "description": "Add tests"},
        headers=auth_headers,
    )
    assert created.status_code == 200
    task_id = created.json()["id"]

    listed = client.get("/tasks/", headers=auth_headers)
    assert [task["id"] for task in listed.json()] == [task_id]

    updated = client.put(
        f"/tasks/{task_id}",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "completed"

    deleted = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert deleted.status_code == 200
    assert client.get("/tasks/", headers=auth_headers).json() == []


def test_user_cannot_modify_another_users_task(client, auth_headers):
    created = client.post(
        "/tasks/", json={"title": "Private"}, headers=auth_headers
    ).json()
    client.post(
        "/register",
        json={"email": "other@example.com", "password": "correct-horse"},
    )
    login = client.post(
        "/login",
        data={"username": "other@example.com", "password": "correct-horse"},
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.put(
        f"/tasks/{created['id']}",
        json={"title": "Unauthorized change"},
        headers=other_headers,
    )
    assert response.status_code == 403


def test_task_validation_rejects_empty_title(client, auth_headers):
    response = client.post("/tasks/", json={"title": ""}, headers=auth_headers)
    assert response.status_code == 422


def test_admin_can_list_users_and_audit_logs(client, admin_headers):
    users = client.get("/tasks/admin/users", headers=admin_headers)
    assert users.status_code == 200
    assert users.json()[0]["role"] == "admin"

    audit_logs = client.get("/tasks/admin/audit-logs", headers=admin_headers)
    assert audit_logs.status_code == 200


def test_regular_user_cannot_access_admin_endpoint(client, auth_headers):
    response = client.get("/tasks/admin/users", headers=auth_headers)
    assert response.status_code == 403
