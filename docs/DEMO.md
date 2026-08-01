# 90-second demonstration guide

Use the deployed Swagger UI and the automated smoke test to record a concise
portfolio demonstration.

1. Show the architecture and CI badges in the repository README.
2. Open the live `/docs` page and highlight authentication, task and health
   endpoint groups.
3. Run `python scripts/smoke_test.py`.
4. Show the successful register, login, CRUD, refresh-token rotation, logout
   and unauthorized-access checks.
5. Open the Render dashboard and show the deployed Docker service, managed
   PostgreSQL database, health check and pre-deploy migration.

Do not display environment-variable values, access tokens, refresh tokens or
database credentials while recording. Keep the finished video under two
minutes and attach it to a GitHub release or a portfolio page, then replace the
demo link in the README with the published URL.
