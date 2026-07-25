import { useCallback, useEffect, useMemo, useState } from "react";

import { financeApi } from "../api/client";
import type { IntelligenceOverview } from "../api/types";
import { ErrorState, LoadingState } from "../components/Feedback";
import { MetricCard } from "../components/MetricCard";
import { TrendChart } from "../components/TrendChart";
import { formatCurrency, formatDate } from "../utils/formatters";
import "./intelligence.css";


function percentLabel(value: string | null): string {
  if (value === null) {
    return "Sem base";
  }
  const numeric = Number(value);
  const signal = numeric > 0 ? "+" : "";
  return `${signal}${numeric.toFixed(2).replace(".", ",")}%`;
}


export function IntelligencePage() {
  const now = useMemo(() => new Date(), []);
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [overview, setOverview] = useState<IntelligenceOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setOverview(await financeApi.getIntelligenceOverview({ year, month }));
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel gerar a inteligencia financeira.",
      );
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">Analise explicavel</span>
          <h1>Inteligencia financeira</h1>
          <p>
            Tendencias, projecoes e alertas calculados pelos seus proprios dados.
          </p>
        </div>
      </header>

      <section className="panel intelligence-filter">
        <label>
          Mes
          <select value={month} onChange={(event) => setMonth(Number(event.target.value))}>
            {Array.from({ length: 12 }, (_, index) => index + 1).map((value) => (
              <option key={value} value={value}>{String(value).padStart(2, "0")}</option>
            ))}
          </select>
        </label>
        <label>
          Ano
          <input
            min="2000"
            max="2100"
            type="number"
            value={year}
            onChange={(event) => setYear(Number(event.target.value))}
          />
        </label>
        <button className="secondary-button" onClick={() => void load()} type="button">
          Atualizar analise
        </button>
      </section>

      {loading ? <LoadingState message="Calculando padroes financeiros..." /> : null}
      {error ? <ErrorState title="Falha na analise" message={error} onRetry={() => void load()} /> : null}

      {overview && !loading && !error ? (
        <div className="intelligence-content">
          <section className="metrics-grid">
            <MetricCard label="Total do mes" value={formatCurrency(overview.summary.current_total)} helper="Valor considerado no periodo" />
            <MetricCard label="Projecao" value={formatCurrency(overview.summary.forecast_total)} helper="Estimativa por ritmo e historico" />
            <MetricCard label="Media historica" value={formatCurrency(overview.summary.historical_average)} helper={`${overview.summary.data_months} meses com dados`} />
            <MetricCard label="Variacao" value={percentLabel(overview.summary.trend_percent)} helper="Comparacao com a media recente" />
          </section>

          <section className="panel intelligence-chart-panel">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Ultimos meses</span>
                <h2>Evolucao usada na analise</h2>
              </div>
            </div>
            <TrendChart items={overview.monthly} />
          </section>

          <section className="intelligence-grid">
            <div className="panel">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">Leitura automatica</span>
                  <h2>Principais insights</h2>
                </div>
              </div>
              <div className="insight-list">
                {overview.insights.map((item) => (
                  <article className={`insight-card ${item.severity}`} key={item.code}>
                    <span>{item.kind}</span>
                    <h3>{item.title}</h3>
                    <p>{item.message}</p>
                    <strong>{item.recommendation}</strong>
                  </article>
                ))}
              </div>
            </div>

            <div className="panel">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">Fora do padrao</span>
                  <h2>Lancamentos incomuns</h2>
                </div>
              </div>
              {overview.anomalies.length ? (
                <div className="intelligence-table-wrap">
                  <table>
                    <thead><tr><th>Data</th><th>Local</th><th>Valor</th><th>Acima da mediana</th></tr></thead>
                    <tbody>
                      {overview.anomalies.map((item) => (
                        <tr key={item.expense_id}>
                          <td>{formatDate(item.purchase_date)}</td>
                          <td><strong>{item.purchase_place}</strong><span>{item.category}</span></td>
                          <td>{formatCurrency(item.amount)}</td>
                          <td>{percentLabel(item.difference_percent)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : <p className="muted-copy">Nenhum lancamento incomum foi identificado neste mes.</p>}
            </div>
          </section>

          <section className="panel">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Padroes mensais</span>
                <h2>Despesas recorrentes detectadas</h2>
              </div>
            </div>
            {overview.recurring.length ? (
              <div className="recurring-grid">
                {overview.recurring.map((item) => (
                  <article className="recurring-card" key={`${item.purchase_place}-${item.category}`}>
                    <strong>{item.purchase_place}</strong>
                    <span>{item.category} - {item.occurrences} ocorrencias</span>
                    <b>{formatCurrency(item.average_amount)} em media</b>
                    <small>Proxima data estimada: {formatDate(item.expected_next_date)}</small>
                  </article>
                ))}
              </div>
            ) : <p className="muted-copy">Ainda nao ha repeticoes suficientes para detectar recorrencias.</p>}
          </section>

          <p className="intelligence-disclaimer">
            As projecoes sao estatisticas deterministicas, nao garantias. Revise os dados antes de tomar decisoes.
          </p>
        </div>
      ) : null}
    </div>
  );
}
