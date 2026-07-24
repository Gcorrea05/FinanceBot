# FinanceBot

FinanceBot e um projeto de controle financeiro pessoal com duas interfaces de responsabilidade distinta.

## Telegram

O bot do Telegram funciona como uma porta operacional simples:

- registrar despesas;
- consultar os cinco lancamentos mais recentes;
- consultar valores a receber;
- marcar uma pendencia compartilhada como recebida.

O Telegram nao concentra relatorios, filtros avancados, graficos ou planejamento mensal.

## Interface web

A interface web concentra visualizacao e manutencao:

- dashboard mensal;
- cadastro, edicao e exclusao de despesas;
- despesas simples, parceladas e compartilhadas;
- valores a receber;
- planejamento mensal de renda, reserva e limite de gastos;
- calculo de limite diario;
- relatorios por periodo, categoria e estabelecimento;
- comparacao mensal e acompanhamento de parcelamentos.

## Regra do planejamento

- despesas simples entram no mes da compra;
- compras parceladas entram pelo vencimento de cada parcela;
- em compras compartilhadas, somente a parte do proprietario entra no gasto;
- a soma da reserva com o limite de gastos nao pode ultrapassar a renda.

## Banco e migrations

As mudancas de schema sao controladas pelo Alembic.

```powershell
python -m scripts.bootstrap_migrations
```

## Executar o Telegram

```powershell
python -m app.main
```

## Executar API e web

Terminal 1:

```powershell
python -m uvicorn app.api.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

## Testes

```powershell
python -m pytest -q
npm --prefix .\frontend run test
```
