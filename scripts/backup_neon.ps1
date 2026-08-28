param(
    [string]$OutputDirectory = "backups"
)

$ErrorActionPreference = "Stop"

if (-not $env:NEON_BACKUP_DATABASE_URL) {
    throw "Set NEON_BACKUP_DATABASE_URL to a standard Neon PostgreSQL connection string before running this script."
}

if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    throw "pg_dump was not found. Install PostgreSQL client tools, then try again."
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputPath = Join-Path $OutputDirectory "securetask-neon-$timestamp.dump"

pg_dump --format=custom --no-owner --file=$outputPath $env:NEON_BACKUP_DATABASE_URL

if ($LASTEXITCODE -ne 0) {
    if (Test-Path -LiteralPath $outputPath) {
        Remove-Item -LiteralPath $outputPath -Force
    }

    throw "pg_dump failed with exit code $LASTEXITCODE. No backup was created."
}

Write-Host "Backup created at $outputPath. Encrypt and store it outside this repository."
