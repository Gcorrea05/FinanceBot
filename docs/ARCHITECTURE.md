# Arquitetura do FinanceBot

## Camadas

O FinanceBot passa a adotar as seguintes fronteiras:

- `app/api`: adaptador HTTP;
- `app/bot`: adaptador Telegram;
- `app/agents`: intermediador seguro para IA;
- `app/services`: casos de uso e coordenacao financeira;
- `app/domain`: regras puras, sem frameworks;
- `app/repositories`: persistencia;
- `app/database/models`: modelos SQLAlchemy;
- `app/events`: eventos financeiros persistentes;
- `app/scheduler`: tarefas automaticas;
- `app/core`: configuracao e logs.

Os models permanecem em `app/database/models`. Move-los apenas para
`app/models` causaria alteracoes sem ganho arquitetural.

Rotas e handlers nao podem acessar repositories ou database. Agents
tambem nao acessam SQL ou models. Essas regras sao verificadas em
`tests/test_architecture_boundaries.py`.

## Eventos

Operacoes financeiras publicam eventos como:

- `expense.created`;
- `expense.updated`;
- `expense.deleted`;
- `budget.updated`;
- `receivable.settled`;
- `receivable.reopened`;
- `import.completed`.

Os eventos sao registrados em `domain_events`. O processamento ocorre
imediatamente e o scheduler tenta novamente os eventos que falharem.

## Scheduler

O worker geral executa:

- alertas e resumos do Telegram;
- retry de eventos;
- relatorio mensal em Excel;
- limpeza de logs;
- backup do SQLite em desenvolvimento.

No PostgreSQL, o backup sera realizado pelos scripts do Batch 16.

## FinanceAgent

O FinanceAgent nao executa SQL. Ele consulta apenas services e possui
capacidades explicitas para:

- gasto mensal;
- previsao;
- orcamento;
- categoria principal;
- valores a receber.

Uma futura LLM deve chamar essas capacidades e nunca receber acesso
direto ao banco.

## Dashboard

O dashboard mostra somente dados realmente modelados:

- gastos;
- limite restante;
- valores a receber;
- previsao;
- categorias;
- calendario de gastos;
- comparacao mensal e anual.

Renda e identificada como planejada. Saldo bancario, receita efetiva e
patrimonio nao sao exibidos porque ainda nao existem contas, receitas
ou ativos no dominio.

## Banco

A migration 0005 adiciona:

- journal de eventos;
- indices compostos;
- foreign keys obrigatorias no SQLite;
- views de recebiveis e parcelas.

Triggers nao calculam saldos ou orcamentos. Regras financeiras em
triggers duplicariam os services e poderiam divergir entre SQLite e
PostgreSQL.

## Logs e configuracoes

Os processos geram `app.log`, `api.log`, `telegram.log` e
`scheduler.log`, com rotacao. Todas as configuracoes sao carregadas por
`app/core/settings.py`. `app/config.py` e `app/api/settings.py` ficam
como adaptadores de compatibilidade.
