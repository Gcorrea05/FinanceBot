$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $root "frontend"

if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    throw "Dependencias do frontend ausentes. Execute npm install dentro de frontend."
}

Set-Location $frontend
npm run dev
