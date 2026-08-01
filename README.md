# SecureTask API

SecureTask API is a production-oriented FastAPI backend demonstrating secure
API design, PostgreSQL persistence, role-based authorization, automated tests,
observability, containerization, CI/CD and Render deployment automation.

## Architecture

```text
Client -> FastAPI -> JWT/RBAC -> SQLAlchemy -> PostgreSQL
                    |             |
                    |             +-> Alembic migrations
                    +-> audit logs, JSON logs and Prometheus metrics

GitHub Actions -> tests + coverage + formatting + Docker build
Render Blueprint -> Docker web service + managed PostgreSQL + generated secrets
```

## Production features

- FastAPI and automatically generated OpenAPI/Swagger documentation
- PostgreSQL with SQLAlchemy connection pooling and Alembic migrations
- JWT authentication with bcrypt password hashing
- Explicit `user` and `admin` roles plus resource-ownership checks
- Request validation, pagination, soft deletion and audit logging
- Structured JSON logs with request correlation IDs
- Prometheus-compatible request count and latency metrics at `/metrics`
- Liveness and database-backed readiness probes
- Non-root Docker image with a container health check
- Unit and API integration tests with a coverage threshold
- GitHub Actions validation against PostgreSQL 16
- Render Blueprint deployment with managed PostgreSQL
- Platform-generated production secrets and database credentials

## API endpoints

| Endpoint | Purpose |
| --- | --- |
| `POST /register` | Register a user |
| `POST /login` | Obtain a JWT access token |
| `POST /tasks/` | Create a user-owned task |
| `GET /tasks/` | List and filter accessible tasks |
| `PUT /tasks/{id}` | Update an owned task |
| `DELETE /tasks/{id}` | Soft-delete an owned task |
| `GET /tasks/admin/users` | List users as an administrator |
| `GET /tasks/admin/audit-logs` | Review audit events as an administrator |
| `GET /health/live` | Process liveness check |
| `GET /health/ready` | Database readiness check |
| `GET /metrics` | Prometheus-compatible metrics |

Interactive documentation is available at `/docs`; the OpenAPI document is at
`/openapi.json`.

## Local development with Docker

1. Copy `.env.example` to `.env`.
2. Replace `POSTGRES_PASSWORD` and `SECURETASK_SECRET_KEY` with strong values.
3. Ensure the password in `SECURETASK_DATABASE_URL` matches
   `POSTGRES_PASSWORD`.
4. Start the complete environment:

```bash
docker compose up --build
```

The API is available at <http://localhost:8000>. Alembic migrations run before
the API begins accepting traffic.

## Local development without Docker

```bash
python -m venv .venv
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Set `SECURETASK_DATABASE_URL` and a secret of at least 16 characters in the
environment before starting the application.

## Testing and quality checks

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
black --check app tests
docker build -t securetaskapi .
```

The tests use an in-memory SQLite database by default for speed. CI overrides
the database URL with PostgreSQL 16, applies every Alembic migration and then
runs the same test suite.

## Render deployment

The root-level `render.yaml` Blueprint deploys the Docker web service and a
managed PostgreSQL database in Render's Frankfurt region. Render injects the
private database connection string and generates a separate JWT secret for the
production service, so local `.env` values are never uploaded.

Create a new Blueprint in Render, connect this GitHub repository and select the
root-level `render.yaml`. The API uses `/health/ready` for platform health
checks, and migrations run before the container starts serving requests.

## Security notes

- Never commit `.env`, environment exports or credentials.
- Store production values in Render's encrypted environment variables or an
  external secret manager.
- Rotate the JWT secret and database credentials according to organizational
  policy.
- Restrict `/metrics` at the ingress or network layer in public deployments.
- Run migrations as a controlled deployment job for multi-replica production
  environments.
