# Importacoes financeiras

O Batch 13 usa um fluxo em tres etapas:

1. leitura da estrutura do arquivo;
2. mapeamento das colunas pelo usuario;
3. pre-visualizacao e confirmacao dos lancamentos validos.

## Principio de compatibilidade

CSV e XLSX nao precisam usar nomes de colunas predefinidos. O FinanceBot exibe as linhas e colunas encontradas e o usuario informa quais colunas representam:

- data;
- descricao principal;
- descricao complementar opcional;
- valor;
- identificador externo opcional.

Tambem podem ser definidos:

- aba da planilha XLSX;
- linha do cabecalho ou ausencia de cabecalho;
- primeira linha de dados;
- formato da data;
- separador decimal;
- regra de sinal para distinguir despesas de creditos ou pagamentos.

O OFX continua automatico porque seus campos de transacao fazem parte do proprio formato.

## Formatos

- CSV com separadores virgula, ponto e virgula, tabulacao ou barra vertical;
- XLSX com selecao da aba;
- OFX com blocos `STMTTRN`.

## Regras

- limite de 5 MB e 5.000 transacoes por arquivo;
- nenhuma coluna e identificada apenas pelo nome;
- valores podem ser importados todos como despesas, somente quando positivos ou somente quando negativos;
- duplicidade usa data, valor, descricao e identificador externo;
- linhas invalidas e ignoradas permanecem no historico para auditoria;
- importacoes geram despesas simples, nao parceladas e nao compartilhadas;
- categoria e forma de pagamento sao escolhidas antes da confirmacao.

## Endpoints

- `POST /api/v1/imports/inspect`;
- `POST /api/v1/imports/preview`;
- `POST /api/v1/imports/{batch_id}/confirm`;
- `GET /api/v1/imports`;
- `GET /api/v1/imports/{batch_id}`.
