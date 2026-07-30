# Auditoria do Batch 17

## Objetivo

Consolidar o FinanceBot em torno do produto real:

- Telegram para registro;
- site para consulta, manutencao, planejamento e relatorios;
- SQLite como banco definitivo local;
- um unico Compose;
- projecao confiavel de compromissos futuros.

## Mantido

- FastAPI, React/Nginx, Telegram e scheduler;
- SQLAlchemy e Alembic;
- SQLite em volume persistente;
- journal de eventos;
- dashboard, inteligencia, importacoes e Excel;
- planejamento mensal, recebiveis e despesas compartilhadas.

## Refatorado

- dinheiro de `Float` para `Numeric(12, 2)` no campo remanescente de compra;
- configuracao SQLite com WAL, foreign keys e busy timeout;
- divisao compartilhada com o proprietario sempre incluido;
- parser deterministico de mensagens naturais;
- recorrencias e ocorrencias futuras separadas de despesas realizadas;
- projecao mensal de comprometido e disponivel;
- planejamento mensal replicavel por varios meses;
- carga inicial da competencia 08/2026;
- backup SQLite sem copia insegura do arquivo ativo;
- Compose consolidado em `compose.yml`.

## Removido

Itens removidos por estarem substituidos ou sem papel operacional na arquitetura final:

- varios instaladores antigos versionados na raiz;
- scripts `check_batch*` antigos;
- Compose de producao anterior;
- scripts locais redundantes para iniciar processos separados;
- FinanceAgent e rota HTTP do agente, que nao faziam parte do produto final;
- teste antigo de fluxo compartilhado substituido pelos testes de dominio atuais.

## Preservacao do banco

A migration `20260729_0006` e incremental. Ela nao recria o banco do zero. A inicializacao executa:

1. Alembic ate `head`;
2. carga idempotente da fatura inicial;
3. `PRAGMA integrity_check`;
4. `PRAGMA foreign_key_check`;
5. verificacao de duplicidades e valores invalidos;
6. confirmacao da revisao Alembic esperada.

## Meios de pagamento

O produto exibe somente:

- Cartao de credito;
- Debito;
- Pix;
- Dinheiro.

Registros historicos com nomes equivalentes sao normalizados sem excluir despesas existentes.

## Evidencias automatizadas

- compilacao Python;
- testes backend;
- typecheck, testes e build do frontend;
- auditoria estrutural;
- validador especifico do Batch 17;
- migration e bootstrap em banco temporario;
- validacao de total da carga 08/2026 em R$ 1.935,58.
