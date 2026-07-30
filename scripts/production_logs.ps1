$ErrorActionPreference = "Stop"

docker compose `
    --env-file .env `
    -f compose.yml `
    logs `
    --tail 250 `
    -f `
    api `
    bot `
    scheduler `
    web `
    migrate
