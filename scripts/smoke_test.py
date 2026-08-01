"""Run a non-destructive end-to-end smoke test against a deployed API."""

import json
import secrets
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def call(base_url, method, path, *, json_body=None, form_body=None, token=None):
    headers = {"Accept": "application/json"}
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    elif form_body is not None:
        data = urlencode(form_body).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(base_url + path, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=90) as response:
            payload = response.read().decode()
            return response.status, parse_payload(payload)
    except HTTPError as error:
        payload = error.read().decode()
        return error.code, parse_payload(payload)


def parse_payload(payload):
    if not payload:
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return {"non_json_response": payload[:200]}


def expect(label, actual, expected, payload=None):
    if actual != expected:
        detail = f"; response={payload!r}" if payload is not None else ""
        raise RuntimeError(f"{label}: expected {expected}, received {actual}{detail}")
    print(f"PASS  {label}: HTTP {actual}")


def main():
    base_url = (
        sys.argv[1] if len(sys.argv) > 1 else "https://securetask-api-stys.onrender.com"
    ).rstrip("/")
    suffix = f"{int(time.time())}-{secrets.token_hex(3)}"
    email = f"smoke-{suffix}@example.com"
    password = secrets.token_urlsafe(24)

    status, _ = call(base_url, "GET", "/tasks/")
    expect("unauthorized access rejected", status, 401)

    status, _ = call(
        base_url,
        "POST",
        "/register",
        json_body={"email": email, "password": password},
    )
    expect("register", status, 200)

    status, tokens = call(
        base_url,
        "POST",
        "/login",
        form_body={"username": email, "password": password},
    )
    expect("login", status, 200, tokens)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    status, task = call(
        base_url,
        "POST",
        "/tasks/",
        json_body={"title": "Production smoke test"},
        token=access_token,
    )
    expect("create task", status, 200)
    task_id = task["id"]

    status, tasks = call(base_url, "GET", "/tasks/", token=access_token)
    expect("retrieve tasks", status, 200)
    if not any(item["id"] == task_id for item in tasks):
        raise RuntimeError("retrieve tasks: created task was not returned")

    status, updated = call(
        base_url,
        "PUT",
        f"/tasks/{task_id}",
        json_body={"status": "completed"},
        token=access_token,
    )
    expect("update task", status, 200)
    if updated["status"] != "completed":
        raise RuntimeError("update task: status was not persisted")

    status, rotated = call(
        base_url,
        "POST",
        "/refresh",
        json_body={"refresh_token": refresh_token},
    )
    expect("rotate refresh token", status, 200)

    status, _ = call(
        base_url, "DELETE", f"/tasks/{task_id}", token=rotated["access_token"]
    )
    expect("delete task", status, 200)

    status, _ = call(
        base_url,
        "POST",
        "/logout",
        json_body={"refresh_token": rotated["refresh_token"]},
    )
    expect("logout", status, 200)
    print("\nProduction smoke test completed successfully.")


if __name__ == "__main__":
    main()
