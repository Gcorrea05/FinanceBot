$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker nao encontrado. Instale ou abra o Docker Desktop."
}

& "$PSScriptRoot\prepare_production_env.ps1"

docker compose `
    --env-file .env `
    -f compose.yml `
    config --quiet

if ($LASTEXITCODE -ne 0) {
    throw "Configuracao do Docker Compose invalida."
}

docker compose `
    --env-file .env `
    -f compose.yml `
    up -d --build

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao iniciar o FinanceBot."
}

$envValues = @{}

Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#=]+?)\s*=(.*)$") {
        $envValues[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$bindAddress = $envValues["PRODUCTION_WEB_BIND_ADDRESS"]
$port = $envValues["PRODUCTION_WEB_PORT"]

$healthUrl = "http://${bindAddress}:${port}/api/v1/health/ready"
$ready = $false

for ($attempt = 1; $attempt -le 30; $attempt++) {
    try {
        $response = Invoke-RestMethod `
            -Uri $healthUrl `
            -TimeoutSec 5

        if ($response.status -eq "ready") {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 2
    }
}

docker compose `
    --env-file .env `
    -f compose.yml `
    ps

if (-not $ready) {
    Write-Host "[ERROR] A API nao ficou pronta no tempo esperado."
    Write-Host "Execute: .\scripts\production_logs.ps1"
    exit 1
}

Write-Host "[OK] FinanceBot iniciado."
Write-Host "[URL] http://${bindAddress}:${port}"
