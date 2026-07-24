# Automacoes do FinanceBot

O Batch 14 adiciona notificacoes proativas pelo Telegram.

## Tipos de mensagem

- resumo diario;
- resumo semanal;
- parcelas vencidas e proximas do vencimento;
- alerta ao atingir o percentual do planejamento mensal.

## Vincular o Telegram

Abra o bot e envie:

```text
/notificacoes
```

O chat atual sera salvo como destino das notificacoes.

## Executar o worker

```powershell
python -m app.automation.worker
```

Ou:

```powershell
.\scripts\run_automations.ps1
```

O worker consulta as configuracoes periodicamente e registra cada
tentativa em `automation_deliveries`. As chaves de deduplicacao impedem
o mesmo resumo ou alerta de ser enviado repetidamente.

## Configuracao

A configuracao fica na pagina **Automacoes** da interface web.

O intervalo de verificacao pode ser ajustado no `.env`:

```text
AUTOMATION_POLL_INTERVAL_SECONDS=60
```

O valor minimo aceito pelo worker e 30 segundos.
