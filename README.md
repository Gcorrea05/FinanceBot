# FinanceBot

FinanceBot e um controle financeiro pessoal local, executado com Docker e SQLite persistente.

## Responsabilidade das interfaces

### Telegram: registro

O Telegram e a porta de entrada dos gastos. O usuario escreve mensagens curtas, por exemplo:

```text
mercado 230
 tablet 1700 parcelado em 10x
presente giron, 300, tomas, yuzo
allianz 390 mensal dia 28
```

O bot interpreta a mensagem, pergunta o meio de pagamento, apresenta um resumo e somente grava depois da confirmacao.

Meios de pagamento aceitos:

- Cartao de credito;
- Debito;
- Pix;
- Dinheiro.

### Site: consulta, planejamento e manutencao

O painel web concentra:

- dashboard e inteligencia financeira;
- consulta, edicao e exclusao de lancamentos;
- valores a receber;
- renda, reserva e limite de gastos por mes;
- projecao de parcelas e despesas recorrentes;
- valor disponivel estimado para os proximos meses;
- importacoes e relatorios em Excel.

Novos gastos cotidianos entram pelo Telegram. O site continua permitindo corrigir ou excluir registros e alterar dados de planejamento.

## Planejamento futuro

Para cada competencia, o sistema calcula:

```text
limite de gastos
- gastos realizados
- parcelas futuras
- despesas recorrentes previstas
= valor disponivel estimado
```

Em compras compartilhadas, somente a parte do proprietario entra como gasto. As demais partes ficam em valores a receber.

## Cartao de credito

A configuracao inicial usa:

- ciclo de 27 a 26;
- fechamento no dia 26;
- parcelas previstas no dia 26;
- competencia inicial da carga do Batch 17: 08/2026.

## Banco de dados

O projeto permanece em SQLite. O banco de producao fica no volume Docker `financebot_data`, com:

- foreign keys habilitadas;
- journal mode WAL;
- busy timeout;
- migrations Alembic;
- backup consistente pela API nativa do SQLite;
- validacao de integridade e foreign keys na inicializacao.

## Executar em producao local

Requisitos: Docker Desktop, Docker Compose V2 e `.env` preenchido.

```powershell
.\scripts\production_up.ps1
```

Acesse:

```text
http://127.0.0.1:8080
```

Comandos operacionais:

```powershell
.\scripts\production_status.ps1
.\scripts\production_logs.ps1
.\scripts\backup_production.ps1
.\scripts\production_down.ps1
```

O comando de parada preserva os volumes. Nunca use `docker compose down -v` neste projeto.

## Validacao

```powershell
python -m compileall -q app scripts tests migrations
python -m scripts.check_batch17
python -m scripts.audit_repository
python -m pytest -q
npm --prefix .\frontend run typecheck
npm --prefix .\frontend run test
npm --prefix .\frontend run build
```

Documentacao complementar:

- `docs/ARCHITECTURE.md`;
- `docs/DEPLOYMENT.md`;
- `docs/BATCH17_AUDIT.md`;
- `docs/API.md`;
- `docs/WEB.md`.
