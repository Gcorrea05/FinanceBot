$ErrorActionPreference = "Stop"

Set-Location (
    Split-Path -Parent $PSScriptRoot
)

python -m app.automation.worker
