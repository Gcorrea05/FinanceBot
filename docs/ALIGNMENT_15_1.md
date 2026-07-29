# Batch 15.1 - Alinhamento funcional

## Relatorio mensal em Excel

A rota `GET /api/v1/exports/monthly.xlsx?year=2026&month=7` gera um arquivo com:

- despesas compradas no mes;
- valor, data, observacao, parcelamento e compartilhamento;
- resumo de quem ainda deve e quanto deve;
- uma segunda aba com o detalhamento por pessoa e compra.

O resumo considera somente pendencias ainda abertas geradas por compras do mes selecionado.

## Consistencia dos valores

A Visao geral usa o mesmo total do Planejamento, considerando:

- sua parte em despesas compartilhadas;
- parcelas pelo mes do vencimento;
- nenhuma limitacao de 100 linhas para calcular o total.

## Recebimentos

A tela exibe recebimentos recentes e permite desfazer uma baixa feita por engano.

## Importacoes

CSV e XLSX podem usar:

- uma unica coluna de valor, escolhendo qual sinal representa despesa; ou
- colunas separadas de debito e credito.

Linhas de credito e estorno sao ignoradas, em vez de serem convertidas em despesas positivas.

## Inteligencia

A media historica considera somente meses com movimento. As anomalias de compras parceladas usam o valor da parcela pertencente ao usuario no mes analisado.
