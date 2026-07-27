# SecureTask API

SecureTask API is a FastAPI task-management backend with JWT authentication,
role-based access control, PostgreSQL, Docker, and Alembic migrations. It runs
locally without Azure resources.

## Features

- JWT authentication and bcrypt password hashing
- User-owned tasks with administrator-only endpoints
- PostgreSQL with SQLAlchemy and Alembic migrations
- Docker Compose for a complete local environment
- Tests and Docker image validation in GitHub Actions

## Run locally with Docker

1. Copy `.env.example` to `.env`.
2. Replace `SECRET_KEY` and `POSTGRES_PASSWORD` with strong local values. The
   password must match the password embedded in `DATABASE_URL`.
3. Start the API and local PostgreSQL database:

   ```bash
   docker compose up --build
   ```

The API is available at http://localhost:8000 and Swagger UI at
http://localhost:8000/docs. Migrations run before the API begins serving
requests.

## Run without Docker

Create and activate a virtual environment, install `requirements.txt`, then
set `SECURETASK_DATABASE_URL` and `SECURETASK_SECRET_KEY` in your environment
(or in `.env`). Apply migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

## Quality checks

```bash
pytest -q
docker build -t securetaskapi .
```

GitHub Actions runs the test suite and checks that the Docker image builds on
pushes and pull requests targeting `main`.

## Future improvements

- Refresh tokens
- Rate limiting
- Monitoring and alerting
