def test_get_tasks_requires_auth(client):
    response = client.get("/tasks/")
    assert response.status_code == 401