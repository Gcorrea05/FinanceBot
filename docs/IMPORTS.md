# Importacoes financeiras

O Batch 13 adiciona importacao em duas etapas:

1. pre-visualizacao do arquivo;
2. confirmacao apenas das linhas validas e nao duplicadas.

## Formatos

- CSV com cabecalho e separadores virgula, ponto e virgula ou tabulacao;
- XLSX usando a primeira aba;
- OFX com blocos `STMTTRN`.

As colunas reconhecidas incluem variantes de data, descricao, valor e identificador externo.

## Regras

- limite de 5 MB e 5.000 transacoes por arquivo;
- valores negativos sao convertidos para valor absoluto de despesa;
- duplicidade usa data, valor, descricao e identificador externo;
- linhas invalidas permanecem no historico para auditoria;
- importacoes geram despesas simples, nao parceladas e nao compartilhadas;
- categoria e forma de pagamento sao escolhidas antes da pre-visualizacao.

## Endpoints

- `POST /api/v1/imports/preview`;
- `POST /api/v1/imports/{batch_id}/confirm`;
- `GET /api/v1/imports`;
- `GET /api/v1/imports/{batch_id}`.
