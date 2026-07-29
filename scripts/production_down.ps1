$ErrorActionPreference = "Stop"

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    down

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao interromper o FinanceBot."
}

Write-Host "[OK] Servicos interrompidos."
Write-Host "[OK] Dados, logs e backups foram preservados."
