$ErrorActionPreference = "Stop"

docker compose `
    --env-file .env `
    -f compose.yml `
    ps

$envValues = @{}

Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*([^#=]+?)\s*=(.*)$") {
        $envValues[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$bindAddress = $envValues["PRODUCTION_WEB_BIND_ADDRESS"]
$port = $envValues["PRODUCTION_WEB_PORT"]

try {
    $response = Invoke-RestMethod `
        -Uri "http://${bindAddress}:${port}/api/v1/health/ready" `
        -TimeoutSec 10

    Write-Host "[OK] API: $($response.status)"
    Write-Host "[URL] http://${bindAddress}:${port}"
} catch {
    Write-Host "[ERROR] API indisponivel: $($_.Exception.Message)"
    exit 1
}
