import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";

import { financeApi } from "../api/client";
import type { FutureOverview, RecurringExpense } from "../api/types";
import { ErrorState, LoadingState } from "../components/Feedback";
import { MetricCard } from "../components/MetricCard";
import { formatCurrency } from "../utils/formatters";
import "./future.css";

const STATUS_LABELS: Record<string, string> = {
  not_configured: "Sem limite configurado",
  healthy: "Dentro do plano",
  attention: "Atencao",
  exceeded: "Limite excedido",
};

function periodLabel(year: number, month: number): string {
  return `${String(month).padStart(2, "0")}/${year}`;
}

export function FuturePage() {
  const now = useMemo(() => new Date(), []);
  const [fromYear, setFromYear] = useState(now.getFullYear());
  const [fromMonth, setFromMonth] = useState(now.getMonth() + 1);
  const [months, setMonths] = useState(12);
  const [overview, setOverview] = useState<FutureOverview | null>(null);
  const [recurring, setRecurring] = useState<RecurringExpense[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [futureResult, recurringResult] = await Promise.all([
        financeApi.getFutureOverview(fromYear, fromMonth, months),
        financeApi.listRecurringExpenses(),
      ]);
      setOverview(futureResult);
      setRecurring(recurringResult);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar os compromissos futuros.");
    } finally {
      setLoading(false);
    }
  }, [fromMonth, fromYear, months]);

  useEffect(() => {
    void load();
  }, [load]);

  function applyPeriod(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void load();
  }

  async function updateRecurring(item: RecurringExpense) {
    setSavingId(item.id);
    setError(null);
    setSuccess(null);
    try {
      const updated = await financeApi.updateRecurringExpense(item.id, {
        amount: item.amount,
        due_day: item.due_day,
        active: item.active,
        auto_post: item.auto_post,
      });
      setRecurring((current) => current.map((row) => row.id === updated.id ? updated : row));
      setSuccess(`${updated.description} atualizado com sucesso.`);
      await load();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Nao foi possivel atualizar o gasto fixo.");
    } finally {
      setSavingId(null);
    }
  }

  const first = overview?.items[0] ?? null;

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">Previsibilidade</span>
          <h1>Proximos meses</h1>
          <p>Veja parcelas, gastos fixos e quanto ainda cabe no seu planejamento.</p>
        </div>
      </header>

      <section className="panel filter-panel">
        <form className="filter-form" onSubmit={applyPeriod}>
          <label>
            Mes inicial
            <select value={fromMonth} onChange={(event) => setFromMonth(Number(event.target.value))}>
              {Array.from({ length: 12 }, (_, index) => index + 1).map((value) => (
                <option key={value} value={value}>{String(value).padStart(2, "0")}</option>
              ))}
            </select>
          </label>
          <label>
            Ano
            <input min="2000" max="2100" type="number" value={fromYear} onChange={(event) => setFromYear(Number(event.target.value))} />
          </label>
          <label>
            Horizonte
            <select value={months} onChange={(event) => setMonths(Number(event.target.value))}>
              {[3, 6, 12, 18, 24].map((value) => <option key={value} value={value}>{value} meses</option>)}
            </select>
          </label>
          <button className="primary-button" type="submit">Atualizar projecao</button>
        </form>
      </section>

      {error ? <ErrorState title="Falha na projecao" message={error} onRetry={() => void load()} /> : null}
      {success ? <div className="inline-alert success">{success}</div> : null}

      {loading || !overview ? (
        <LoadingState message="Calculando compromissos futuros..." />
      ) : (
        <>
          {first ? (
            <section className="metric-grid future-metrics">
              <MetricCard label={`Comprometido em ${periodLabel(first.year, first.month)}`} value={formatCurrency(first.committed_total)} helper="Realizado, parcelas e fixos previstos" />
              <MetricCard label="Parcelas do periodo" value={formatCurrency(first.installment_total)} helper="Compras parceladas com vencimento no mes" />
              <MetricCard label="Gastos fixos previstos" value={formatCurrency(first.recurring_total)} helper="Ocorrencias ainda nao lancadas" />
              <MetricCard label="Ainda pode gastar" value={first.available_to_spend === null ? "-" : formatCurrency(first.available_to_spend)} helper={first.available_to_spend === null ? "Configure o limite no Planejamento" : "Limite mensal menos compromissos"} />
            </section>
          ) : null}

          <section className="panel future-table-panel">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Linha do tempo</span>
                <h2>Compromissos por competencia</h2>
              </div>
            </div>
            <div className="table-wrapper">
              <table>
                <thead><tr><th>Competencia</th><th>Realizado</th><th>Parcelas</th><th>Fixos</th><th>Comprometido</th><th>Limite</th><th>Disponivel</th><th>Status</th></tr></thead>
                <tbody>
                  {overview.items.map((item) => (
                    <tr key={`${item.year}-${item.month}`}>
                      <td className="strong-cell">{periodLabel(item.year, item.month)}</td>
                      <td>{formatCurrency(item.recorded_total)}</td>
                      <td>{formatCurrency(item.installment_total)}</td>
                      <td>{formatCurrency(item.recurring_total)}</td>
                      <td className="strong-cell">{formatCurrency(item.committed_total)}</td>
                      <td>{item.spending_limit === null ? "-" : formatCurrency(item.spending_limit)}</td>
                      <td className={item.available_to_spend !== null && Number(item.available_to_spend) < 0 ? "negative-cell" : ""}>{item.available_to_spend === null ? "-" : formatCurrency(item.available_to_spend)}</td>
                      <td><span className={`future-status ${item.status}`}>{STATUS_LABELS[item.status] ?? item.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="panel recurring-panel">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Gastos programados</span>
                <h2>Fixos mensais</h2>
              </div>
              <span className="status-badge">Cadastro pelo Telegram</span>
            </div>
            <div className="recurring-list">
              {recurring.length === 0 ? <p>Nenhum gasto fixo cadastrado.</p> : recurring.map((item) => (
                <article className="recurring-card" key={item.id}>
                  <div>
                    <strong>{item.description}</strong>
                    <span>{item.category} · {item.payment_method}</span>
                  </div>
                  <label>
                    Valor
                    <input inputMode="decimal" value={item.amount} onChange={(event) => setRecurring((current) => current.map((row) => row.id === item.id ? { ...row, amount: event.target.value.replace(",", ".") } : row))} />
                  </label>
                  <label>
                    Dia
                    <input min="1" max="31" type="number" value={item.due_day} onChange={(event) => setRecurring((current) => current.map((row) => row.id === item.id ? { ...row, due_day: Number(event.target.value) } : row))} />
                  </label>
                  <label className="checkbox-row compact-check"><input checked={item.active} type="checkbox" onChange={(event) => setRecurring((current) => current.map((row) => row.id === item.id ? { ...row, active: event.target.checked } : row))} />Ativo</label>
                  <button className="secondary-button" disabled={savingId === item.id} onClick={() => void updateRecurring(item)} type="button">{savingId === item.id ? "Salvando..." : "Salvar"}</button>
                </article>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
