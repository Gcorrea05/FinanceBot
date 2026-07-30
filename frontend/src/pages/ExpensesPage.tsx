import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";

import { financeApi } from "../api/client";
import type { Expense, ExpenseListResponse, ExpenseMutationPayload } from "../api/types";
import { ExpenseForm } from "../components/ExpenseForm";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { ExpenseTable } from "../components/ExpenseTable";

const PAGE_SIZE = 10;

export function ExpensesPage() {
  const now = useMemo(() => new Date(), []);
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [offset, setOffset] = useState(0);
  const [data, setData] = useState<ExpenseListResponse | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [paymentMethods, setPaymentMethods] = useState<string[]>([]);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    try {
      setData(await financeApi.listExpenses({ limit: PAGE_SIZE, offset, month, year }));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Nao foi possivel carregar as despesas.");
    }
  }, [month, offset, year]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    void Promise.all([financeApi.listCategories(), financeApi.listPaymentMethods()])
      .then(([categoryResponse, paymentResponse]) => {
        setCategories(categoryResponse.items.map((item) => item.name));
        setPaymentMethods(paymentResponse.items.map((item) => item.name));
      })
      .catch((referenceError: unknown) => setError(referenceError instanceof Error ? referenceError.message : "Nao foi possivel carregar os dados de referencia."));
  }, []);

  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / PAGE_SIZE));

  function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOffset(0);
    if (offset === 0) void load();
  }

  async function save(payload: ExpenseMutationPayload) {
    if (!editingExpense) return;
    setSaving(true);
    setError(null);
    try {
      await financeApi.updateExpense(editingExpense.id, payload);
      setSuccess("Despesa atualizada com sucesso.");
      setEditingExpense(null);
      await load();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Nao foi possivel atualizar a despesa.");
    } finally {
      setSaving(false);
    }
  }

  async function remove(expense: Expense) {
    if (!window.confirm(`Excluir a despesa de ${expense.purchase_place}? Esta acao nao pode ser desfeita.`)) return;
    setError(null);
    setSuccess(null);
    try {
      await financeApi.deleteExpense(expense.id);
      setSuccess("Despesa excluida com sucesso.");
      if (data && data.items.length === 1 && offset > 0) setOffset(Math.max(0, offset - PAGE_SIZE));
      else await load();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Nao foi possivel excluir a despesa.");
    }
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">Historico e manutencao</span>
          <h1>Despesas</h1>
          <p>Os novos gastos entram pelo Telegram. Aqui voce consulta, corrige ou exclui lancamentos.</p>
        </div>
        <span className="status-badge">Registro pelo Telegram</span>
      </header>
      {success ? <div className="inline-alert success">{success}</div> : null}
      <section className="panel filter-panel">
        <form className="filter-form" onSubmit={applyFilters}>
          <label>Mes<select value={month} onChange={(event) => setMonth(Number(event.target.value))}>{Array.from({ length: 12 }, (_, index) => index + 1).map((value) => <option key={value} value={value}>{String(value).padStart(2, "0")}</option>)}</select></label>
          <label>Ano<input min="2000" max="2100" type="number" value={year} onChange={(event) => setYear(Number(event.target.value))} /></label>
          <button className="primary-button" type="submit">Aplicar filtro</button>
        </form>
      </section>
      <section className="panel">
        {error ? <ErrorState title="Falha ao carregar despesas" message={error} onRetry={() => void load()} /> : !data ? <LoadingState /> : data.items.length ? (
          <>
            <ExpenseTable expenses={data.items} onDelete={(expense) => void remove(expense)} onEdit={setEditingExpense} />
            <div className="pagination">
              <button className="secondary-button" type="button" disabled={offset === 0} onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}>Anterior</button>
              <span>Pagina {currentPage} de {totalPages}</span>
              <button className="secondary-button" type="button" disabled={offset + PAGE_SIZE >= data.total} onClick={() => setOffset(offset + PAGE_SIZE)}>Proxima</button>
            </div>
          </>
        ) : <EmptyState title="Nenhuma despesa encontrada" message="Nao ha lancamentos para o periodo selecionado." />}
      </section>
      {editingExpense ? (
        <ExpenseForm
          key={editingExpense.id}
          busy={saving}
          categories={categories}
          expense={editingExpense}
          paymentMethods={paymentMethods}
          onCancel={() => setEditingExpense(null)}
          onSubmit={save}
        />
      ) : null}
    </div>
  );
}
