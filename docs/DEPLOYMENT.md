# Implantacao local com Docker

## Estrutura

O FinanceBot usa um unico arquivo Compose: `compose.yml`.

Servicos:

- `migrate`: aplica Alembic, carga inicial idempotente e validacao do SQLite;
- `api`: FastAPI;
- `bot`: Telegram;
- `scheduler`: automacoes e despesas recorrentes;
- `web`: React servido pelo Nginx.

Somente `127.0.0.1:8080` e publicado. API e banco permanecem internos.

## Persistencia

Volumes:

- `financebot_data`: SQLite e relatorios;
- `financebot_backups`: backups;
- `financebot_logs`: logs.

Parar containers nao apaga esses volumes. Nao use `docker compose down -v`.

## Configuracao

Valores reais sao lidos exclusivamente de `.env`. O `.env.example` e somente modelo e nunca deve receber o token real.

Prepare as variaveis ausentes sem substituir as existentes:

```powershell
.\scripts\prepare_production_env.ps1
```

## Primeira subida ou atualizacao

```powershell
.\scripts\production_up.ps1
```

O fluxo executado e:

```text
build
-> migrate
-> seed idempotente da fatura 08/2026
-> integrity_check e foreign_key_check
-> API healthy
-> bot, scheduler e web
```

Acesse `http://127.0.0.1:8080`.

## Status e logs

```powershell
.\scripts\production_status.ps1
.\scripts\production_logs.ps1
```

`migrate` terminar com `Exited (0)` e esperado.

## Backup

```powershell
.\scripts\backup_production.ps1
.\scripts\list_production_backups.ps1
```

O backup usa `sqlite3.Connection.backup`, seguido de verificacao de integridade.

## Restauracao

```powershell
.\scripts\restore_production.ps1 `
    -BackupName "financebot-AAAAMMDD-HHMMSS.db"
```

A restauracao exige confirmacao explicita e os processos que escrevem no banco devem estar parados.

## Parada segura

```powershell
.\scripts\production_down.ps1
```

## Atualizacao de codigo

```powershell
.\scripts\backup_production.ps1
git pull --ff-only origin main
.\scripts\production_up.ps1
```

## Computador ligado

Para operacao continua local, o Docker Desktop precisa iniciar com o Windows e o computador nao pode entrar em suspensao.
