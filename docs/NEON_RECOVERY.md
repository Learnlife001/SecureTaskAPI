# Neon backup and recovery

SecureTask API uses Neon PostgreSQL in production. The production connection
string is stored only in Render as `SECURETASK_DATABASE_URL`; do not place it
in this repository, a GitHub Action log, or a committed `.env` file.

## Recovery routine

Before a production release, schema change, or other destructive operation:

1. Open the Neon Console and select the `securetask-api` project and its
   production `main` branch.
2. Open **Backup & Restore** and create a named snapshot, for example
   `before-release-YYYY-MM-DD`.
3. Record the snapshot name and intended change in the release or pull request.
4. Make the change through a pull request and verify
   `https://sta.greglabs.nl/health/ready` after deployment.

For a recovery drill, first create a separate branch from the snapshot or a
point in the restore window. Inspect it there before restoring production. A
restore changes the production branch data, so it requires explicit approval.

## Optional encrypted export

For an independent export, install PostgreSQL client tools and set the
standard Neon URL in the local `NEON_BACKUP_DATABASE_URL` environment variable.
Run:

```powershell
./scripts/backup_neon.ps1
```

The script writes a custom-format `pg_dump` file beneath the ignored
`backups/` directory. Encrypt and store that file in an approved backup
location; delete the local copy when it is no longer needed.

## Retention decision

Neon's Free plan has limited instant-restore history and one manual snapshot.
Before real user data is stored, select a paid Neon plan with a recovery window
and scheduled snapshots that match the data-retention requirements. Do not rely
on a free-tier restore window as the only production backup.
