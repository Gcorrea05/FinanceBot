import { useEffect, useState } from "react";

import { ApiError, financeApi } from "../api/client";
import type { ImportBatch, ReferenceItem } from "../api/types";
import { ErrorState } from "../components/Feedback";
import { formatCurrency, formatDate } from "../utils/formatters";
import "./imports.css";


export function ImportsPage() {
  const [categories, setCategories] = useState<ReferenceItem[]>([]);
  const [payments, setPayments] = useState<ReferenceItem[]>([]);
  const [category, setCategory] = useState("");
  const [payment, setPayment] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<ImportBatch | null>(null);
  const [history, setHistory] = useState<ImportBatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadReferencesAndHistory() {
    try {
      const [categoryResponse, paymentResponse, historyResponse] = await Promise.all([
        financeApi.listCategories(),
        financeApi.listPaymentMethods(),
        financeApi.listImports(),
      ]);
      setCategories(categoryResponse.items);
      setPayments(paymentResponse.items);
      setCategory((current) => current || categoryResponse.items.at(-1)?.name || "");
      setPayment((current) => current || paymentResponse.items[0]?.name || "");
      setHistory(historyResponse.items);
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Nao foi possivel carregar a tela de importacoes.");
    }
  }

  useEffect(() => {
    void loadReferencesAndHistory();
  }, []);

  async function handlePreview(event: React.FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Selecione um arquivo CSV, XLSX ou OFX.");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      setPreview(await financeApi.previewImport(file, category, payment));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Falha ao analisar o arquivo.");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirm() {
    if (!preview) return;
    setLoading(true);
    setError(null);
    try {
      const confirmed = await financeApi.confirmImport(preview.id);
      setPreview(confirmed);
      setMessage(`${confirmed.imported_rows} despesa(s) importada(s).`);
      await loadReferencesAndHistory();
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Falha ao confirmar a importacao.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page-stack imports-page">
      <header className="page-header">
        <div>
          <span className="eyebrow">Entrada de dados</span>
          <h1>Importacoes</h1>
          <p>Carregue CSV, XLSX ou OFX, revise duplicidades e confirme somente os lancamentos validos.</p>
        </div>
      </header>

      {error ? (<ErrorState title="Falha na importacao" message={error} />) : null}
      {message ? (
        <div className="feedback-card" role="status">
          <strong>Importacao concluida</strong>
          <p>{message}</p>
        </div>
      ) : null}

      <form className="panel import-form" onSubmit={handlePreview}>
        <label>
          Arquivo
          <input accept=".csv,.xlsx,.ofx" type="file" onChange={(event) => setFile(event.target.files?.[0] || null)} />
        </label>
        <label>
          Categoria padrao
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((item) => <option key={item.name}>{item.name}</option>)}
          </select>
        </label>
        <label>
          Forma de pagamento
          <select value={payment} onChange={(event) => setPayment(event.target.value)}>
            {payments.map((item) => <option key={item.name}>{item.name}</option>)}
          </select>
        </label>
        <button className="primary-button" disabled={loading} type="submit">
          {loading ? "Analisando..." : "Pre-visualizar"}
        </button>
      </form>

      {preview ? (
        <section className="panel">
          <div className="section-heading import-summary-heading">
            <div>
              <span className="eyebrow">Arquivo analisado</span>
              <h2>{preview.filename}</h2>
            </div>
            {preview.status === "previewed" && preview.ready_rows > 0 ? (
              <button className="primary-button" disabled={loading} onClick={handleConfirm} type="button">
                Confirmar {preview.ready_rows} lancamento(s)
              </button>
            ) : null}
          </div>
          <div className="import-metrics">
            <strong>{preview.total_rows}<span>Total</span></strong>
            <strong>{preview.ready_rows}<span>Prontos</span></strong>
            <strong>{preview.duplicate_rows}<span>Duplicados</span></strong>
            <strong>{preview.invalid_rows}<span>Invalidos</span></strong>
            <strong>{preview.imported_rows}<span>Importados</span></strong>
          </div>
          <div className="table-wrapper">
            <table>
              <thead><tr><th>Linha</th><th>Data</th><th>Descricao</th><th>Valor</th><th>Status</th></tr></thead>
              <tbody>
                {preview.rows.map((row) => (
                  <tr key={row.id}>
                    <td>{row.row_number}</td>
                    <td>{row.purchase_date ? formatDate(row.purchase_date) : "-"}</td>
                    <td><strong>{row.purchase_place || "Linha invalida"}</strong><small>{row.error_message}</small></td>
                    <td>{row.purchase_value ? formatCurrency(row.purchase_value) : "-"}</td>
                    <td><span className={`import-status ${row.status}`}>{row.status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}

      <section className="panel">
        <div className="section-heading"><div><span className="eyebrow">Auditoria</span><h2>Historico</h2></div></div>
        {history.length === 0 ? <p className="muted-copy">Nenhuma importacao realizada.</p> : (
          <div className="import-history">
            {history.map((batch) => (
              <article key={batch.id}>
                <div><strong>{batch.filename}</strong><span>{formatDate(batch.created_at)} - {batch.source_type.toUpperCase()}</span></div>
                <div><strong>{batch.imported_rows || batch.ready_rows}</strong><span>{batch.status === "completed" ? "importados" : "prontos"}</span></div>
              </article>
            ))}
          </div>
        )}
      </section>
    </section>
  );
}
