$ErrorActionPreference = "Stop"

docker compose `
    --env-file .env `
    -f docker-compose.prod.yml `
    run `
    --rm `
    --no-deps `
    api `
    python `
    -c `
    "from pathlib import Path; root=Path('/app/backups/manual'); root.mkdir(parents=True, exist_ok=True); [print(path.name) for path in sorted(root.glob('*.db'), reverse=True)]"
