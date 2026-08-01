def test_app_starts(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "SecureTaskAPI"


def test_health_and_metrics_endpoints(client):
    assert client.get("/health/live").json() == {"status": "ok"}
    readiness = client.get("/health/ready")
    assert readiness.status_code == 200
    assert readiness.json()["database"] == "available"

    metrics = client.get("/metrics", headers={"X-Metrics-Token": "test-metrics-token"})
    assert metrics.status_code == 200
    assert "securetask_http_requests_total" in metrics.text


def test_metrics_requires_token(client):
    response = client.get("/metrics")
    assert response.status_code == 401


def test_openapi_documents_security_scheme(client):
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "SecureTask API"
    assert "OAuth2PasswordBearer" in schema["components"]["securitySchemes"]
