import {
  useCallback,
  useEffect,
  useState,
  type FormEvent,
} from "react";

import { financeApi } from "../api/client";
import type {
  AutomationDelivery,
  AutomationMessage,
  AutomationSettings,
  AutomationSettingsPayload,
} from "../api/types";
import {
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import "./automations.css";


const WEEKDAYS = [
  "Segunda-feira",
  "Terca-feira",
  "Quarta-feira",
  "Quinta-feira",
  "Sexta-feira",
  "Sabado",
  "Domingo",
];


function messageLabel(
  kind: string,
): string {
  const labels: Record<string, string> = {
    daily_summary: "Resumo diario",
    weekly_summary: "Resumo semanal",
    installment_reminder: "Vencimentos",
    budget_alert: "Alerta de limite",
  };

  return labels[kind] ?? kind;
}


export function AutomationsPage() {
  const [
    settings,
    setSettings,
  ] = useState<AutomationSettings | null>(
    null
  );

  const [
    preview,
    setPreview,
  ] = useState<AutomationMessage[]>([]);

  const [
    deliveries,
    setDeliveries,
  ] = useState<AutomationDelivery[]>([]);

  const [loading, setLoading] = useState(
    true
  );
  const [saving, setSaving] = useState(
    false
  );
  const [running, setRunning] = useState(
    false
  );

  const [error, setError] = useState<
    string | null
  >(null);
  const [success, setSuccess] = useState<
    string | null
  >(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [
        settingsResult,
        previewResult,
        historyResult,
      ] = await Promise.all([
        financeApi.getAutomationSettings(),
        financeApi.previewAutomations(),
        financeApi.listAutomationDeliveries(),
      ]);

      setSettings(settingsResult);
      setPreview(previewResult.items);
      setDeliveries(historyResult.items);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel carregar as automacoes.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  function update<
    K extends keyof AutomationSettings,
  >(
    key: K,
    value: AutomationSettings[K],
  ) {
    setSettings((current) => (
      current
        ? {
            ...current,
            [key]: value,
          }
        : current
    ));
  }

  async function save(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!settings) {
      return;
    }

    const payload: AutomationSettingsPayload = {
      enabled: settings.enabled,
      timezone: settings.timezone,
      daily_summary_enabled:
        settings.daily_summary_enabled,
      daily_summary_hour:
        settings.daily_summary_hour,
      weekly_summary_enabled:
        settings.weekly_summary_enabled,
      weekly_summary_weekday:
        settings.weekly_summary_weekday,
      weekly_summary_hour:
        settings.weekly_summary_hour,
      installment_reminders_enabled:
        settings.installment_reminders_enabled,
      installment_reminder_days:
        settings.installment_reminder_days,
      reminder_hour: settings.reminder_hour,
      budget_alerts_enabled:
        settings.budget_alerts_enabled,
      budget_alert_threshold:
        settings.budget_alert_threshold,
    };

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await (
        financeApi.saveAutomationSettings(
          payload
        )
      );
      const previewResult = await (
        financeApi.previewAutomations()
      );

      setSettings(result);
      setPreview(previewResult.items);
      setSuccess(
        "Configuracoes salvas."
      );
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Nao foi possivel salvar as configuracoes.",
      );
    } finally {
      setSaving(false);
    }
  }

  async function runNow() {
    setRunning(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await (
        financeApi.runAutomationsNow()
      );
      const history = await (
        financeApi.listAutomationDeliveries()
      );

      setDeliveries(history.items);
      setSuccess(
        `${result.sent} mensagem(ns) enviada(s).`
      );
    } catch (runError) {
      setError(
        runError instanceof Error
          ? runError.message
          : "Nao foi possivel executar as automacoes.",
      );
    } finally {
      setRunning(false);
    }
  }

  async function disconnect() {
    setError(null);
    setSuccess(null);

    try {
      const result = await (
        financeApi.disconnectTelegram()
      );

      setSettings(result);
      setSuccess(
        "Telegram desvinculado."
      );
    } catch (disconnectError) {
      setError(
        disconnectError instanceof Error
          ? disconnectError.message
          : "Nao foi possivel desvincular o Telegram.",
      );
    }
  }

  if (error && !settings) {
    return (
      <ErrorState
        title="Falha nas automacoes"
        message={error}
        onRetry={() => void load()}
      />
    );
  }

  if (loading || !settings) {
    return (
      <LoadingState
        message="Carregando automacoes..."
      />
    );
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">
            Notificacoes programadas
          </span>
          <h1>Automacoes</h1>
          <p>
            Receba resumos, vencimentos
            e alertas pelo Telegram.
          </p>
        </div>

        <span
          className={
            settings.enabled
              ? "automation-status enabled"
              : "automation-status"
          }
        >
          {settings.enabled
            ? "Ativas"
            : "Desativadas"}
        </span>
      </header>

      {error ? (
        <div
          className="inline-alert error"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      {success ? (
        <div
          className="inline-alert success"
          role="status"
        >
          {success}
        </div>
      ) : null}

      <div className="automation-layout">
        <section className="panel">
          <div className="section-heading">
            <div>
              <span className="eyebrow">
                Agendamento
              </span>
              <h2>Configuracoes</h2>
            </div>
          </div>

          <form
            className="automation-form"
            onSubmit={save}
          >
            <label className="toggle-row">
              <input
                checked={settings.enabled}
                type="checkbox"
                onChange={(event) =>
                  update(
                    "enabled",
                    event.target.checked,
                  )
                }
              />
              <span>
                <strong>
                  Ativar automacoes
                </strong>
                <small>
                  O worker precisa estar
                  em execucao.
                </small>
              </span>
            </label>

            <label>
              Fuso horario
              <input
                required
                value={settings.timezone}
                onChange={(event) =>
                  update(
                    "timezone",
                    event.target.value,
                  )
                }
              />
            </label>

            <fieldset>
              <legend>Resumo diario</legend>

              <label className="toggle-row">
                <input
                  checked={
                    settings.daily_summary_enabled
                  }
                  type="checkbox"
                  onChange={(event) =>
                    update(
                      "daily_summary_enabled",
                      event.target.checked,
                    )
                  }
                />
                <span>
                  Enviar todos os dias
                </span>
              </label>

              <label>
                Hora
                <input
                  min="0"
                  max="23"
                  type="number"
                  value={
                    settings.daily_summary_hour
                  }
                  onChange={(event) =>
                    update(
                      "daily_summary_hour",
                      Number(event.target.value),
                    )
                  }
                />
              </label>
            </fieldset>

            <fieldset>
              <legend>Resumo semanal</legend>

              <label className="toggle-row">
                <input
                  checked={
                    settings.weekly_summary_enabled
                  }
                  type="checkbox"
                  onChange={(event) =>
                    update(
                      "weekly_summary_enabled",
                      event.target.checked,
                    )
                  }
                />
                <span>
                  Enviar uma vez por semana
                </span>
              </label>

              <div className="form-row">
                <label>
                  Dia
                  <select
                    value={
                      settings.weekly_summary_weekday
                    }
                    onChange={(event) =>
                      update(
                        "weekly_summary_weekday",
                        Number(event.target.value),
                      )
                    }
                  >
                    {WEEKDAYS.map(
                      (label, index) => (
                        <option
                          key={label}
                          value={index}
                        >
                          {label}
                        </option>
                      ),
                    )}
                  </select>
                </label>

                <label>
                  Hora
                  <input
                    min="0"
                    max="23"
                    type="number"
                    value={
                      settings.weekly_summary_hour
                    }
                    onChange={(event) =>
                      update(
                        "weekly_summary_hour",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>
              </div>
            </fieldset>

            <fieldset>
              <legend>
                Parcelas e vencimentos
              </legend>

              <label className="toggle-row">
                <input
                  checked={
                    settings.installment_reminders_enabled
                  }
                  type="checkbox"
                  onChange={(event) =>
                    update(
                      "installment_reminders_enabled",
                      event.target.checked,
                    )
                  }
                />
                <span>
                  Lembrar parcelas pendentes
                </span>
              </label>

              <div className="form-row">
                <label>
                  Antecedencia em dias
                  <input
                    min="0"
                    max="30"
                    type="number"
                    value={
                      settings.installment_reminder_days
                    }
                    onChange={(event) =>
                      update(
                        "installment_reminder_days",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>

                <label>
                  Hora
                  <input
                    min="0"
                    max="23"
                    type="number"
                    value={
                      settings.reminder_hour
                    }
                    onChange={(event) =>
                      update(
                        "reminder_hour",
                        Number(event.target.value),
                      )
                    }
                  />
                </label>
              </div>
            </fieldset>

            <fieldset>
              <legend>
                Alerta de planejamento
              </legend>

              <label className="toggle-row">
                <input
                  checked={
                    settings.budget_alerts_enabled
                  }
                  type="checkbox"
                  onChange={(event) =>
                    update(
                      "budget_alerts_enabled",
                      event.target.checked,
                    )
                  }
                />
                <span>
                  Avisar ao atingir o limite
                </span>
              </label>

              <label>
                Percentual de alerta
                <input
                  min="1"
                  max="100"
                  type="number"
                  value={
                    settings.budget_alert_threshold
                  }
                  onChange={(event) =>
                    update(
                      "budget_alert_threshold",
                      Number(event.target.value),
                    )
                  }
                />
              </label>
            </fieldset>

            <button
              className="primary-button"
              disabled={saving}
              type="submit"
            >
              {saving
                ? "Salvando..."
                : "Salvar configuracoes"}
            </button>
          </form>
        </section>

        <div className="automation-side">
          <section className="panel">
            <span className="eyebrow">
              Telegram
            </span>
            <h2>
              {settings.telegram_connected
                ? "Conectado"
                : "Nao conectado"}
            </h2>

            {settings.telegram_connected ? (
              <>
                <p>
                  O chat esta pronto para
                  receber notificacoes.
                </p>

                <div className="button-row">
                  <button
                    className="secondary-button"
                    disabled={running}
                    type="button"
                    onClick={() =>
                      void runNow()
                    }
                  >
                    {running
                      ? "Enviando..."
                      : "Enviar teste agora"}
                  </button>

                  <button
                    className="danger-button"
                    type="button"
                    onClick={() =>
                      void disconnect()
                    }
                  >
                    Desvincular
                  </button>
                </div>
              </>
            ) : (
              <p>
                Abra o bot no Telegram e
                envie o comando
                <code>/notificacoes</code>.
              </p>
            )}
          </section>

          <section className="panel">
            <span className="eyebrow">
              Pre-visualizacao
            </span>
            <h2>Mensagens atuais</h2>

            <div className="automation-preview">
              {preview.length ? (
                preview.map((item) => (
                  <article
                    key={item.kind}
                    className="preview-message"
                  >
                    <strong>
                      {item.title}
                    </strong>
                    <pre>
                      {item.message}
                    </pre>
                  </article>
                ))
              ) : (
                <p>
                  Nenhuma mensagem aplicavel
                  neste momento.
                </p>
              )}
            </div>
          </section>
        </div>
      </div>

      <section className="panel automation-history">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              Historico
            </span>
            <h2>Ultimos envios</h2>
          </div>
        </div>

        {deliveries.length ? (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Status</th>
                  <th>Data</th>
                  <th>Detalhe</th>
                </tr>
              </thead>
              <tbody>
                {deliveries.map((item) => (
                  <tr key={item.id}>
                    <td>
                      {messageLabel(item.kind)}
                    </td>
                    <td>
                      <span
                        className={
                          `delivery-status ${item.status}`
                        }
                      >
                        {item.status}
                      </span>
                    </td>
                    <td>
                      {new Date(
                        item.sent_at
                        ?? item.created_at
                      ).toLocaleString("pt-BR")}
                    </td>
                    <td>
                      {item.error_message
                        ?? item.message
                          .split("\n")[0]}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>
            Nenhuma notificacao enviada.
          </p>
        )}
      </section>
    </div>
  );
}
