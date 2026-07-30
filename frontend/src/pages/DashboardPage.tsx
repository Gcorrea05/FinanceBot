import {
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { financeApi } from "../api/client";
import type { DashboardOverview } from "../api/types";
import { BreakdownBars } from "../components/BreakdownBars";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import { ExpenseTable } from "../components/ExpenseTable";
import { MetricCard } from "../components/MetricCard";
import { formatCurrency } from "../utils/formatters";
import "./dashboard.css";


function currentPeriod(): {
  month: number;
  year: number;
} {
  const now = new Date();
  return {
    month: now.getMonth() + 1,
    year: now.getFullYear(),
  };
}


function formatChange(value: string | null): string {
  if (value === null) {
    return "Sem base comparavel";
  }
  const numeric = Number(value);
  const prefix = numeric > 0 ? "+" : "";
  return `${prefix}${numeric.toFixed(2)}%`;
}


export function DashboardPage() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [apiStatus, setApiStatus] = useState("");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      const period = currentPeriod();
      const [health, dashboard] = await Promise.all([
        financeApi.ready(),
        financeApi.getDashboard(
          period.year,
          period.month,
        ),
      ]);
      setApiStatus(health.status);
      setData(dashboard);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel carregar o painel.",
      );
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (error) {
    return (
      <PageFrame
        title="Visao geral"
        subtitle="Centro de decisao financeira do mes atual."
      >
        <ErrorState
          title="API indisponivel"
          message={error}
          onRetry={() => void load()}
        />
      </PageFrame>
    );
  }

  if (!data) {
    return (
      <PageFrame
        title="Visao geral"
        subtitle="Centro de decisao financeira do mes atual."
      >
        <LoadingState />
      </PageFrame>
    );
  }

  return (
    <PageFrame
      title="Visao geral"
      subtitle="Centro de decisao financeira do mes atual."
      status={
        apiStatus === "ready"
          ? "API conectada"
          : apiStatus
      }
    >
      <section className="metric-grid">
        <MetricCard
          label="Gasto no mes"
          value={formatCurrency(data.spent)}
          helper="Sua parte e parcelas do mes"
        />
        <MetricCard
          label="Limite restante"
          value={
            data.budget_remaining === null
              ? "Nao configurado"
              : formatCurrency(data.budget_remaining)
          }
          helper={`Situacao: ${data.budget_status}`}
        />
        <MetricCard
          label="Valores a receber"
          value={formatCurrency(data.receivables)}
          helper="Pendencias ainda abertas"
        />
        <MetricCard
          label="Projecao do mes"
          value={formatCurrency(data.forecast_total)}
          helper="Estimativa explicavel, nao saldo bancario"
        />
      </section>

      <section className="dashboard-comparison-grid">
        <article className="panel compact-panel">
          <span className="eyebrow">Comparacao</span>
          <h2>Mes anterior</h2>
          <strong>
            {formatCurrency(
              data.comparison.previous_month_total,
            )}
          </strong>
          <p>
            {formatChange(
              data.comparison.previous_month_change_percent,
            )}
          </p>
        </article>

        <article className="panel compact-panel">
          <span className="eyebrow">Comparacao</span>
          <h2>Mesmo mes do ano anterior</h2>
          <strong>
            {formatCurrency(
              data.comparison.year_ago_total,
            )}
          </strong>
          <p>
            {formatChange(
              data.comparison.year_ago_change_percent,
            )}
          </p>
        </article>

        <article className="panel compact-panel">
          <span className="eyebrow">Planejamento</span>
          <h2>Renda planejada</h2>
          <strong>
            {data.planned_income === null
              ? "Nao configurada"
              : formatCurrency(data.planned_income)}
          </strong>
          <p>Nao representa saldo em conta.</p>
        </article>
      </section>

      <section className="dashboard-analysis-grid">
        <article className="panel">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Distribuicao</span>
              <h2>Gastos por categoria</h2>
            </div>
          </div>
          <BreakdownBars items={data.categories} />
        </article>

        <article className="panel">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Calendario</span>
              <h2>Dias com maior gasto</h2>
            </div>
          </div>
          <DailyHeatmap items={data.daily} />
        </article>
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Conferencia rapida</span>
            <h2>Ultimos lancamentos</h2>
          </div>
        </div>

        {data.recent_expenses.length ? (
          <ExpenseTable expenses={data.recent_expenses} />
        ) : (
          <EmptyState
            title="Nenhuma despesa neste mes"
            message="Registre uma despesa pelo Telegram."
          />
        )}
      </section>
    </PageFrame>
  );
}


function DailyHeatmap({
  items,
}: {
  items: DashboardOverview["daily"];
}) {
  const totals = new Map(
    items.map((item) => [
      item.day,
      Number(item.total),
    ]),
  );
  const maximum = Math.max(
    ...items.map((item) => Number(item.total)),
    1,
  );

  return (
    <div className="daily-heatmap">
      {Array.from(
        { length: 31 },
        (_, index) => index + 1,
      ).map((day) => {
        const total = totals.get(day) ?? 0;
        const intensity = Math.min(total / maximum, 1);

        return (
          <div
            className="heatmap-day"
            key={day}
            style={{ opacity: 0.3 + intensity * 0.7 }}
            title={`Dia ${day}: ${formatCurrency(total)}`}
          >
            <span>{day}</span>
            <small>
              {total > 0 ? formatCurrency(total) : "-"}
            </small>
          </div>
        );
      })}
    </div>
  );
}


interface PageFrameProps {
  title: string;
  subtitle: string;
  status?: string;
  children: ReactNode;
}


function PageFrame({
  title,
  subtitle,
  status,
  children,
}: PageFrameProps) {
  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">FinanceBot Web</span>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        {status ? (
          <span className="status-badge">{status}</span>
        ) : null}
      </header>
      {children}
    </div>
  );
}
