# FinanceBot Web

A interface web complementa o Telegram. O bot continua focado em registro rapido e consulta operacional; o painel web concentra visualizacao e manutencao dos dados.

## Funcionalidades atuais

- dashboard do mes atual;
- lista de despesas com filtro mensal e paginacao;
- cadastro de despesas simples, parceladas e compartilhadas;
- edicao completa de despesas;
- exclusao mediante confirmacao;
- valores a receber com baixa de pendencias;
- tratamento de API indisponivel;
- testes automatizados do cliente HTTP e dos formularios.

## Regra de seguranca da edicao

Uma despesa com parcela marcada como paga ou valor compartilhado marcado como recebido nao pode ser reestruturada. A API retorna conflito para impedir que um historico financeiro ja confirmado seja apagado durante a edicao.

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

Relatorios analiticos, orcamento, importacoes e autenticacao ainda nao fazem parte da interface.
