param(
    [Parameter(Mandatory = $true)]
    [string]$BackupName
)

$ErrorActionPreference = "Stop"

if ($BackupName -match "[\\/]" ) {
    throw "Informe apenas o nome do arquivo existente no volume de backups."
}

$confirmation = Read-Host "A restauracao substituira o banco atual. Digite RESTAURAR"

if ($confirmation -ne "RESTAURAR") {
    throw "Restauracao cancelada."
}

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    stop `
    api `
    bot `
    scheduler

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao parar os servicos."
}

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    run `
    --rm `
    --no-deps `
    api `
    python `
    -m `
    scripts.restore_sqlite `
    --backup `
    "/app/backups/manual/$BackupName"

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao restaurar o banco."
}

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    start `
    api `
    bot `
    scheduler

if ($LASTEXITCODE -ne 0) {
    throw "Banco restaurado, mas houve falha ao reiniciar os servicos."
}

Write-Host "[OK] Banco restaurado."
