# Security Policy

## System and Scope

SecureTask API is an open-source FastAPI reference implementation for task
management. The public surface includes the API, its OpenAPI documentation,
and the Render deployment configuration. This policy covers the application
code, Docker configuration, GitHub Actions workflows, and documented
deployment paths.

## Threat Model and Trust Boundaries

Internet clients can submit registration, login, refresh-token, and task
requests. JWT signing keys, the metrics token, and database credentials are
trusted secrets and must remain outside source control. Render injects
production secrets and database credentials. Application authorization,
request validation, token validation, and database ownership checks are the
security boundaries between an untrusted request and protected data.

## Security Invariants

- Secrets, environment files, and real user data must not be committed.
- Protected task and administrative operations must authenticate and authorize
  the caller before accessing or changing data.
- Refresh tokens must be revocable and must not be accepted after expiration
  or revocation.
- Production metrics must require the configured metrics token.
- Production deployment must use HTTPS and provider-managed secret storage.

## Reporting a Vulnerability

Please do not disclose suspected vulnerabilities in public issues. Use
GitHub's private vulnerability reporting for this repository when it is
available; otherwise contact the repository owner privately through GitHub
before sharing details. Include affected endpoint or component, reproduction
steps, impact, and any suggested mitigation. Do not include credentials,
tokens, personal data, or production database contents.

## Reportable Findings and Severity Context

Report findings that could expose secrets or user data, bypass authentication
or authorization, allow token forgery or replay, enable unintended database
access, or permit remote code execution. Severity depends on realistic
reachability and impact against the public deployment.

## Out of Scope

The intentionally public API documentation and OpenAPI schema are not
vulnerabilities by themselves. Local `.env` files and user-managed cloud
accounts are outside repository support, although accidental disclosure of
their contents in this repository is in scope.

## Known Limitations

The free Render service may spin down after inactivity, and the free database
does not provide durable backups. Production users should choose an
availability and backup plan appropriate to their data and risk requirements.
