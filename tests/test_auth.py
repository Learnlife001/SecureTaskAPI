def test_login_invalid_credentials(client):
    response = client.post(
        "/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert response.status_code == 401


def test_user_can_register_login_and_create_task(client):
    register_response = client.post(
        "/register",
        json={"email": "user@example.com", "password": "correct-horse"},
    )
    assert register_response.status_code == 200
    assert "hashed_password" not in register_response.json()

    login_response = client.post(
        "/login",
        data={"username": "user@example.com", "password": "correct-horse"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    task_response = client.post(
        "/tasks/",
        json={"title": "First task"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert task_response.status_code == 200
    assert task_response.json()["title"] == "First task"
