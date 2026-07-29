# FinanceBot em producao

## Arquitetura

A implantacao final executa quatro processos independentes:

- API FastAPI;
- bot do Telegram;
- scheduler geral;
- frontend React servido pelo Nginx.

Antes deles, o servico `migrate` aplica as migrations ate
`20260724_0005`.

O SQLite fica no volume persistente `financebot_data`.
Logs, relatorios e backups usam volumes separados.

## Fonte das configuracoes

Valores reais sao carregados exclusivamente do arquivo `.env`.

O `.env.example` nao e utilizado pela aplicacao nem pelo Docker
Compose. Ele permanece somente como modelo de documentacao.

O script abaixo preserva as configuracoes existentes e adiciona
somente as chaves de producao que estiverem ausentes:

```powershell
.\scripts\prepare_production_env.ps1
```

O token permanece em:

```text
TELEGRAM_TOKEN=...
```

## Requisitos

- Docker Desktop;
- Docker Compose V2;
- `.env` preenchido;
- `TELEGRAM_TOKEN` preenchido no `.env`;
- porta 8080 livre.

## Inicializacao

```powershell
.\scripts\production_up.ps1
```

Acesse:

```text
http://127.0.0.1:8080
```

A API e o banco nao possuem portas publicadas. O Nginx encaminha
`/api` pela rede interna do Docker.

## Status e logs

```powershell
.\scripts\production_status.ps1
.\scripts\production_logs.ps1
```

## Parada

```powershell
.\scripts\production_down.ps1
```

O comando preserva os volumes.

## Backup manual

```powershell
.\scripts\backup_production.ps1
```

Para listar backups:

```powershell
.\scripts\list_production_backups.ps1
```

## Restauracao

Primeiro, liste os arquivos e copie o nome desejado:

```powershell
.\scripts\list_production_backups.ps1
```

Depois:

```powershell
.\scripts\restore_production.ps1 `
    -BackupName "financebot-20260726-120000.db"
```

A restauracao exige a confirmacao textual `RESTAURAR`.

## Atualizacao

Antes de atualizar:

```powershell
.\scripts\backup_production.ps1
git pull --ff-only origin main
.\scripts\production_up.ps1
```

O container `migrate` atualiza o banco antes da API, do bot e do
scheduler.

## Limite de exposicao

O endereco padrao e `127.0.0.1`. Portanto, o site fica acessivel
somente na propria maquina.

Nao altere `PRODUCTION_WEB_BIND_ADDRESS` para `0.0.0.0` sem VPN,
HTTPS e autenticacao externa.
