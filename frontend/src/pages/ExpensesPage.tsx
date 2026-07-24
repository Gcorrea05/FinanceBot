import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";

import { financeApi } from "../api/client";
import type { ExpenseListResponse } from "../api/types";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { ExpenseTable } from "../components/ExpenseTable";

const PAGE_SIZE = 10;

export function ExpensesPage() {
  const now = useMemo(() => new Date(), []);
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState<ExpenseListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);

    try {
      const response = await financeApi.listExpenses({
        limit: PAGE_SIZE,
        offset,
        month,
        year,
      });
      setData(response);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel carregar as despesas.",
      );
    }
  }, [month, offset, year]);

  useEffect(() => {
    void load();
  }, [load]);

  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOffset(0);
    void load();
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">Historico</span>
          <h1>Despesas</h1>
          <p>Consulte os lancamentos por mes e ano.</p>
        </div>
      </header>

      <section className="panel filter-panel">
        <form className="filter-form" onSubmit={applyFilters}>
          <label>
            Mes
            <select value={month} onChange={(event) => setMonth(Number(event.target.value))}>
              {Array.from({ length: 12 }, (_, index) => index + 1).map((value) => (
                <option key={value} value={value}>
                  {String(value).padStart(2, "0")}
                </option>
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
          <button className="primary-button" type="submit">
            Aplicar filtro
          </button>
        </form>
      </section>

      <section className="panel">
        {error ? (
          <ErrorState title="Falha ao carregar despesas" message={error} onRetry={() => void load()} />
        ) : !data ? (
          <LoadingState />
        ) : data.items.length ? (
          <>
            <ExpenseTable expenses={data.items} />
            <div className="pagination">
              <button
                className="secondary-button"
                type="button"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
              >
                Anterior
              </button>
              <span>
                Pagina {currentPage} de {totalPages}
              </span>
              <button
                className="secondary-button"
                type="button"
                disabled={offset + PAGE_SIZE >= data.total}
                onClick={() => setOffset(offset + PAGE_SIZE)}
              >
                Proxima
              </button>
            </div>
          </>
        ) : (
          <EmptyState
            title="Nenhuma despesa encontrada"
            message="Nao ha lancamentos para o periodo selecionado."
          />
        )}
      </section>
    </div>
  );
}
