$ErrorActionPreference = "Stop"

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$containerPath = "/app/backups/manual/financebot-$timestamp.db"

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    run `
    --rm `
    --no-deps `
    api `
    python `
    -m `
    scripts.backup_sqlite `
    --output `
    $containerPath

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao criar o backup."
}

Write-Host "[OK] Backup salvo no volume financebot_backups."
Write-Host "[ARQUIVO] $containerPath"
