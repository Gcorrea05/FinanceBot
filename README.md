# FinanceBot

FinanceBot e um projeto de controle financeiro pessoal com duas interfaces de responsabilidade distinta.

## Telegram

O bot do Telegram funciona como uma porta operacional simples:

- registrar despesas;
- consultar os cinco lancamentos mais recentes;
- consultar valores a receber;
- marcar uma pendencia compartilhada como recebida.

O Telegram nao concentra relatorios, filtros avancados, graficos, orcamentos ou cadastros administrativos.

## Interface web planejada

A futura interface web sera responsavel por:

- visao mensal e historica;
- filtros por periodo, categoria e estabelecimento;
- parcelamentos;
- orcamentos;
- graficos e comparacoes;
- importacoes;
- exportacoes;
- edicao completa dos dados.

## Execucao local

1. Crie o ambiente virtual.
2. Instale `requirements-dev.txt`.
3. Copie `.env.example` para `.env`.
4. Informe `TELEGRAM_TOKEN`.
5. Execute:

```powershell
python -m app.main
```

## Testes

```powershell
python -m pytest -q
```
