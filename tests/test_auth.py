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
    assert login_response.json()["refresh_token"]

    task_response = client.post(
        "/tasks/",
        json={"title": "First task"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert task_response.status_code == 200
    assert task_response.json()["title"] == "First task"


def test_refresh_token_rotation_and_logout(client):
    client.post(
        "/register",
        json={"email": "rotation@example.com", "password": "correct-horse"},
    )
    login = client.post(
        "/login",
        data={"username": "rotation@example.com", "password": "correct-horse"},
    )
    original_refresh = login.json()["refresh_token"]

    refreshed = client.post("/refresh", json={"refresh_token": original_refresh})
    assert refreshed.status_code == 200
    rotated_refresh = refreshed.json()["refresh_token"]
    assert rotated_refresh != original_refresh

    reused = client.post("/refresh", json={"refresh_token": original_refresh})
    assert reused.status_code == 401

    logout = client.post("/logout", json={"refresh_token": rotated_refresh})
    assert logout.status_code == 200
    assert logout.json() == {"message": "Logged out"}

    after_logout = client.post("/refresh", json={"refresh_token": rotated_refresh})
    assert after_logout.status_code == 401


def test_refresh_token_cannot_access_protected_api(client):
    client.post(
        "/register",
        json={"email": "token-type@example.com", "password": "correct-horse"},
    )
    login = client.post(
        "/login",
        data={"username": "token-type@example.com", "password": "correct-horse"},
    )
    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {login.json()['refresh_token']}"},
    )
    assert response.status_code == 401


def test_invalid_refresh_token_is_rejected(client):
    response = client.post(
        "/refresh", json={"refresh_token": "not-a-valid-refresh-token"}
    )
    assert response.status_code == 401
