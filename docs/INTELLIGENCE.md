# Inteligencia financeira

O Batch 15 adiciona analises deterministicas e explicaveis sobre os dados do FinanceBot.

## Capacidades

- projecao do total mensal por ritmo de gastos e media historica;
- comparacao com os cinco meses anteriores;
- alertas de orcamento e concentracao por categoria;
- deteccao robusta de lancamentos fora do padrao por mediana e MAD;
- deteccao de estabelecimentos recorrentes em pelo menos tres meses;
- recomendacoes acompanhadas das evidencias que as originaram.

## Limites

O recurso nao usa um modelo generativo e nao substitui orientacao financeira profissional. As projecoes sao estimativas estatisticas, podem ser afetadas por dados incompletos e nunca devem ser tratadas como garantia.

## API

`GET /api/v1/intelligence/overview?year=2026&month=7`

A consulta nao grava dados e nao exige migration nova.
