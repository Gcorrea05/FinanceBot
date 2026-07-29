# Politica de seguranca

## Segredos

Nunca versione:

- `.env`;
- token do Telegram;
- chaves de IA;
- bancos SQLite;
- arquivos de backup;
- arquivos de log.

O `.env.example` deve conter somente nomes de variaveis e valores
ficticios. A aplicacao nao o carrega.

## Rede

A configuracao final publica apenas o frontend/Nginx em
`127.0.0.1:8080`.

A API e o banco ficam restritos a rede interna do Docker.

## Exposicao externa

O FinanceBot armazena informacoes financeiras pessoais. Nao o
exponha diretamente na internet sem:

- HTTPS;
- autenticacao;
- VPN ou proxy de acesso;
- politica de atualizacoes;
- backups testados.

## Segredo exposto

Caso um token seja publicado:

1. revogue o token imediatamente;
2. gere um novo token;
3. atualize o `.env`;
4. reinicie os containers;
5. remova o segredo do historico Git quando necessario.
