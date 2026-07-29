$ErrorActionPreference = "Stop"

$envPath = Join-Path (Get-Location) ".env"

if (-not (Test-Path $envPath)) {
    throw "Arquivo .env nao encontrado. O FinanceBot nao le .env.example."
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$content = Get-Content $envPath -Raw

$requiredEntries = [ordered]@{
    "PRODUCTION_DATABASE_URL" = "sqlite:////app/data/finance.db"
    "PRODUCTION_API_CORS_ORIGINS" = "http://127.0.0.1:8080,http://localhost:8080"
    "PRODUCTION_LOG_DIRECTORY" = "/app/logs"
    "PRODUCTION_REPORT_DIRECTORY" = "/app/data/reports"
    "PRODUCTION_SQLITE_BACKUP_DIRECTORY" = "/app/backups/sqlite"
    "PRODUCTION_SQLITE_BACKUP_ENABLED" = "true"
    "PRODUCTION_EXPOSE_API_DOCS" = "false"
    "PRODUCTION_TRUSTED_HOSTS" = "localhost,127.0.0.1,testserver"
    "PRODUCTION_WEB_BIND_ADDRESS" = "127.0.0.1"
    "PRODUCTION_WEB_PORT" = "8080"
}

$added = @()

foreach ($name in $requiredEntries.Keys) {
    $pattern = "(?m)^\s*" + [regex]::Escape($name) + "\s*="

    if ($content -match $pattern) {
        continue
    }

    if ($content -and -not $content.EndsWith("`n")) {
        $content += "`n"
    }

    $content += "$name=$($requiredEntries[$name])`n"
    $added += $name
}

[System.IO.File]::WriteAllText(
    $envPath,
    $content,
    $utf8NoBom
)

$envValues = @{}

Get-Content $envPath | ForEach-Object {
    if ($_ -match "^\s*([^#=]+?)\s*=(.*)$") {
        $envValues[$matches[1].Trim()] = $matches[2].Trim()
    }
}

if (
    -not $envValues.ContainsKey("TELEGRAM_TOKEN") -or
    [string]::IsNullOrWhiteSpace($envValues["TELEGRAM_TOKEN"])
) {
    throw "TELEGRAM_TOKEN nao esta preenchido no arquivo .env."
}

if ($added.Count -gt 0) {
    Write-Host "[OK] Configuracoes de producao adicionadas ao .env:"
    $added | ForEach-Object {
        Write-Host "  - $_"
    }
} else {
    Write-Host "[OK] O .env ja possui as configuracoes de producao."
}

Write-Host "[OK] TELEGRAM_TOKEN identificado no .env."
Write-Host "[OK] Nenhum valor foi carregado de .env.example."
