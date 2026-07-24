# FinanceBot Web

A interface web complementa o Telegram. O bot continua focado em registro e consulta rapida; o painel web concentra visualizacao e navegacao sobre os dados.

## Escopo do Batch 9

- React com TypeScript;
- Vite como servidor de desenvolvimento e build;
- dashboard do mes atual;
- lista de despesas com filtro mensal e paginacao;
- valores a receber com baixa de pendencias;
- tratamento de API indisponivel;
- testes do cliente HTTP, formatadores e navegacao principal.

## Executar localmente

Terminal 1, na raiz:

```powershell
python -m uvicorn app.api.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Acesse `http://127.0.0.1:5173`.

## Configuracao

Copie `frontend/.env.example` para `frontend/.env` quando precisar alterar o endereco da API.

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

## Limites atuais

O Batch 9 e deliberadamente consultivo. Cadastro completo, edicao, exclusao e relatorios analiticos entram nos proximos batches.
