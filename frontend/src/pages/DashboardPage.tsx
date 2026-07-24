import { useCallback, useEffect, useState, type ReactNode } from "react";

import { financeApi } from "../api/client";
import type { Expense, ReceivableSummaryResponse } from "../api/types";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { ExpenseTable } from "../components/ExpenseTable";
import { MetricCard } from "../components/MetricCard";
import { formatCurrency } from "../utils/formatters";

interface DashboardData {
  expenses: Expense[];
  expenseTotal: number;
  receivables: ReceivableSummaryResponse;
  apiStatus: string;
}

function currentPeriod(): { month: number; year: number } {
  const now = new Date();
  return { month: now.getMonth() + 1, year: now.getFullYear() };
}

export function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);

    try {
      const period = currentPeriod();
      const [health, expenses, receivables] = await Promise.all([
        financeApi.ready(),
        financeApi.listExpenses({
          limit: 100,
          offset: 0,
          month: period.month,
          year: period.year,
        }),
        financeApi.listReceivables(),
      ]);

      const expenseTotal = expenses.items.reduce(
        (total, expense) => total + Number(expense.purchase_value),
        0,
      );

      setData({
        expenses: expenses.items,
        expenseTotal,
        receivables,
        apiStatus: health.status,
      });
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
      <PageFrame title="Visao geral" subtitle="Resumo financeiro do mes atual.">
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
      <PageFrame title="Visao geral" subtitle="Resumo financeiro do mes atual.">
        <LoadingState />
      </PageFrame>
    );
  }

  return (
    <PageFrame
      title="Visao geral"
      subtitle="Resumo financeiro do mes atual."
      status={data.apiStatus === "ready" ? "API conectada" : data.apiStatus}
    >
      <section className="metric-grid">
        <MetricCard
          label="Gasto no mes"
          value={formatCurrency(data.expenseTotal)}
          helper={`${data.expenses.length} lancamento(s) carregado(s)`}
        />
        <MetricCard
          label="Valores a receber"
          value={formatCurrency(data.receivables.total_general)}
          helper={`${data.receivables.people.length} pessoa(s) com pendencia`}
        />
        <MetricCard
          label="Ultimo lancamento"
          value={
            data.expenses[0]
              ? formatCurrency(data.expenses[0].purchase_value)
              : formatCurrency(0)
          }
          helper={data.expenses[0]?.purchase_place ?? "Nenhuma despesa no periodo"}
        />
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">Conferencia rapida</span>
            <h2>Ultimos lancamentos</h2>
          </div>
        </div>

        {data.expenses.length ? (
          <ExpenseTable expenses={data.expenses.slice(0, 5)} />
        ) : (
          <EmptyState
            title="Nenhuma despesa neste mes"
            message="Registre uma despesa pelo Telegram para ela aparecer aqui."
          />
        )}
      </section>
    </PageFrame>
  );
}

interface PageFrameProps {
  title: string;
  subtitle: string;
  status?: string;
  children: ReactNode;
}

function PageFrame({ title, subtitle, status, children }: PageFrameProps) {
  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">FinanceBot Web</span>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
        {status ? <span className="status-badge">{status}</span> : null}
      </header>
      {children}
    </div>
  );
}
