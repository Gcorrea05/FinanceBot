# Arquitetura do FinanceBot

## Fronteiras

- `app/bot`: adaptador Telegram, sem acesso direto ao banco;
- `app/api`: contrato HTTP usado pelo site;
- `app/domain`: regras puras de dinheiro, parcelamento, divisao e interpretacao;
- `app/services`: casos de uso e transacoes financeiras;
- `app/repositories`: persistencia SQLAlchemy;
- `app/database/models`: schema relacional;
- `app/events`: journal persistente de eventos;
- `app/automation`: worker e automacoes;
- `app/core`: configuracao, logs e infraestrutura compartilhada.

Handlers e rotas chamam services. Regras financeiras nao ficam no Telegram, no React, em triggers ou no Compose.

## Fluxo de registro pelo Telegram

```text
mensagem livre
-> NaturalExpenseParser
-> rascunho validado
-> pergunta do meio de pagamento
-> confirmacao
-> ExpenseService ou RecurringExpenseService
-> SQLite
-> evento persistente
```

O parser e deterministico e nao depende de LLM. Mensagens ambiguas nao sao gravadas automaticamente.

## Fluxo do site

O site consulta a API para dashboard, lancamentos, planejamento, recorrencias, projecoes e relatorios. Ele permite manutencao dos registros e configuracoes, mas o cadastro cotidiano fica concentrado no Telegram.

## Planejamento e futuro

O dominio separa:

- despesa efetiva;
- parcela de uma compra;
- programacao recorrente;
- ocorrencia futura de uma recorrencia;
- planejamento mensal.

Uma ocorrencia futura nao vira despesa realizada antes do processamento previsto. Chaves unicas tornam o scheduler idempotente.

## SQLite

API, bot e scheduler compartilham o arquivo `/app/data/finance.db` por volume nomeado. Para reduzir contencao:

- `PRAGMA foreign_keys=ON`;
- `PRAGMA journal_mode=WAL`;
- `PRAGMA busy_timeout`;
- `PRAGMA synchronous=NORMAL`;
- transacoes curtas;
- uma migration executada antes dos processos de longa duracao.

Dinheiro usa `Numeric(12, 2)` e `Decimal`; `FLOAT` nao e usado nos novos fluxos financeiros.

## Compose

O arquivo unico e `compose.yml`:

```text
migrate -> aplica migrations, carga idempotente e validacao
api     -> FastAPI
bot     -> Telegram
scheduler -> recorrencias, eventos e alertas
web     -> React/Nginx e unica porta exposta
```

O SQLite nao e um servico separado. Ele fica no volume persistente compartilhado pelos tres processos backend.

## Eventos e rastreabilidade

Operacoes financeiras publicam eventos persistentes, como:

- `expense.created`;
- `expense.updated`;
- `expense.deleted`;
- `budget.updated`;
- `receivable.settled`;
- `recurring_expense.created`;
- `recurring_expense.occurrence_posted`.

O journal permite auditoria e reprocessamento sem colocar regra financeira nos adaptadores.
