$ErrorActionPreference = "Stop"

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    logs `
    --tail 250 `
    -f `
    api `
    bot `
    scheduler `
    web `
    migrate
