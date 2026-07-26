import { useEffect, useMemo, useState } from "react";

import { ApiError, financeApi } from "../api/client";
import type {
  ImportAmountMode,
  ImportBatch,
  ImportColumnMapping,
  ImportDateFormat,
  ImportDecimalSeparator,
  ImportInspection,
  ReferenceItem,
} from "../api/types";
import { ErrorState } from "../components/Feedback";
import { formatCurrency, formatDate } from "../utils/formatters";
import "./imports.css";


function numberOrNull(value: string): number | null {
  return value === "" ? null : Number(value);
}

export function ImportsPage() {
  const [categories, setCategories] = useState<ReferenceItem[]>([]);
  const [payments, setPayments] = useState<ReferenceItem[]>([]);
  const [category, setCategory] = useState("");
  const [payment, setPayment] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [inspection, setInspection] = useState<ImportInspection | null>(null);
  const [preview, setPreview] = useState<ImportBatch | null>(null);
  const [history, setHistory] = useState<ImportBatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [sheetName, setSheetName] = useState("");
  const [headerRow, setHeaderRow] = useState(1);
  const [dataStartRow, setDataStartRow] = useState(2);
  const [dateColumn, setDateColumn] = useState("");
  const [descriptionColumn, setDescriptionColumn] = useState("");
  const [descriptionExtraColumn, setDescriptionExtraColumn] = useState("");
  const [amountLayout, setAmountLayout] = useState<"single" | "debit_credit">("single");
  const [amountColumn, setAmountColumn] = useState("");
  const [debitColumn, setDebitColumn] = useState("");
  const [creditColumn, setCreditColumn] = useState("");
  const [externalIdColumn, setExternalIdColumn] = useState("");
  const [dateFormat, setDateFormat] = useState<ImportDateFormat>("auto");
  const [decimalSeparator, setDecimalSeparator] = useState<ImportDecimalSeparator>("auto");
  const [amountMode, setAmountMode] = useState<ImportAmountMode>("positive");

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

  const columnOptions = useMemo(() => {
    if (!inspection) return [];
    const header = headerRow > 0 ? inspection.rows[headerRow - 1] || [] : [];
    return Array.from({ length: inspection.max_columns }, (_, index) => ({
      value: String(index),
      label: header[index]
        ? `${index + 1} - ${header[index]}`
        : `Coluna ${index + 1}`,
    }));
  }, [inspection, headerRow]);

  function resetMapping() {
    setDateColumn("");
    setDescriptionColumn("");
    setDescriptionExtraColumn("");
    setAmountLayout("single");
    setAmountColumn("");
    setDebitColumn("");
    setCreditColumn("");
    setExternalIdColumn("");
    setHeaderRow(1);
    setDataStartRow(2);
    setDateFormat("auto");
    setDecimalSeparator("auto");
    setAmountMode("positive");
  }

  async function inspectSelectedFile(selectedSheet?: string) {
    if (!file) {
      setError("Selecione um arquivo CSV, XLSX ou OFX.");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);
    setPreview(null);
    try {
      const result = await financeApi.inspectImport(file, selectedSheet);
      setInspection(result);
      setSheetName(result.selected_sheet || "");
      resetMapping();
      if (!result.mapping_required) {
        setHeaderRow(1);
        setDataStartRow(2);
      }
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Falha ao ler a estrutura do arquivo.");
    } finally {
      setLoading(false);
    }
  }

  async function handleInspect(event: React.FormEvent) {
    event.preventDefault();
    await inspectSelectedFile(sheetName || undefined);
  }

  async function handleSheetChange(value: string) {
    setSheetName(value);
    await inspectSelectedFile(value);
  }

  function buildMapping(): ImportColumnMapping | undefined {
    if (!inspection?.mapping_required) return undefined;
    const parsedDate = numberOrNull(dateColumn);
    const parsedDescription = numberOrNull(descriptionColumn);
    const parsedAmount = numberOrNull(amountColumn);
    const parsedDebit = numberOrNull(debitColumn);
    const parsedCredit = numberOrNull(creditColumn);
    if (parsedDate === null || parsedDescription === null) {
      throw new Error("Mapeie as colunas de data e descricao.");
    }
    if (amountLayout === "single" && parsedAmount === null) {
      throw new Error("Selecione a coluna unica de valor.");
    }
    if (amountLayout === "debit_credit" && parsedDebit === null) {
      throw new Error("Selecione a coluna de debito.");
    }
    const descriptions = [parsedDescription];
    const extra = numberOrNull(descriptionExtraColumn);
    if (extra !== null && extra !== parsedDescription) descriptions.push(extra);
    return {
      sheet_name: inspection.selected_sheet,
      header_row: headerRow > 0 ? headerRow : null,
      data_start_row: dataStartRow,
      date_column: parsedDate,
      description_columns: descriptions,
      amount_column: amountLayout === "single" ? parsedAmount : null,
      debit_column: amountLayout === "debit_credit" ? parsedDebit : null,
      credit_column: amountLayout === "debit_credit" ? parsedCredit : null,
      external_id_column: numberOrNull(externalIdColumn),
      date_format: dateFormat,
      decimal_separator: decimalSeparator,
      amount_mode: amountMode,
    };
  }

  async function handlePreview() {
    if (!file || !inspection) {
      setError("Leia a estrutura do arquivo antes de pre-visualizar.");
      return;
    }
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      setPreview(await financeApi.previewImport(file, category, payment, buildMapping()));
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : caught instanceof Error
            ? caught.message
            : "Falha ao analisar o arquivo.",
      );
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
          <p>O FinanceBot nao exige nomes de colunas. Voce escolhe as colunas sem depender dos nomes do arquivo. Creditos e estornos podem ser ignorados com seguranca.</p>
        </div>
      </header>

      {error ? <ErrorState title="Falha na importacao" message={error} /> : null}
      {message ? (
        <div className="feedback-card" role="status">
          <strong>Importacao concluida</strong>
          <p>{message}</p>
        </div>
      ) : null}

      <form className="panel import-form" onSubmit={handleInspect}>
        <label>
          Arquivo
          <input
            accept=".csv,.xlsx,.ofx"
            type="file"
            onChange={(event) => {
              setFile(event.target.files?.[0] || null);
              setInspection(null);
              setPreview(null);
              setSheetName("");
              resetMapping();
            }}
          />
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
        <button className="primary-button" disabled={loading || !file} type="submit">
          {loading ? "Lendo..." : "Ler estrutura"}
        </button>
      </form>

      {inspection ? (
        <section className="panel mapping-panel">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Estrutura detectada</span>
              <h2>{file?.name}</h2>
              <p>{inspection.total_rows} linha(s), {inspection.max_columns} coluna(s).</p>
            </div>
          </div>

          {inspection.sheets.length > 0 ? (
            <label className="mapping-sheet">
              Aba da planilha
              <select value={sheetName} onChange={(event) => void handleSheetChange(event.target.value)}>
                {inspection.sheets.map((sheet) => <option key={sheet}>{sheet}</option>)}
              </select>
            </label>
          ) : null}

          {inspection.mapping_required ? (
            <>
              <div className="mapping-grid">
                <label>
                  Linha do cabecalho
                  <input
                    min="0"
                    type="number"
                    value={headerRow}
                    onChange={(event) => {
                      const value = Math.max(0, Number(event.target.value));
                      setHeaderRow(value);
                      setDataStartRow(value > 0 ? value + 1 : 1);
                    }}
                  />
                  <small>Use 0 quando o arquivo nao possuir cabecalho.</small>
                </label>
                <label>
                  Primeira linha de dados
                  <input min="1" type="number" value={dataStartRow} onChange={(event) => setDataStartRow(Math.max(1, Number(event.target.value)))} />
                </label>
                <label>
                  Coluna da data
                  <select value={dateColumn} onChange={(event) => setDateColumn(event.target.value)}>
                    <option value="">Selecione</option>
                    {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </label>
                <label>
                  Coluna da descricao
                  <select value={descriptionColumn} onChange={(event) => setDescriptionColumn(event.target.value)}>
                    <option value="">Selecione</option>
                    {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </label>
                <label>
                  Descricao complementar
                  <select value={descriptionExtraColumn} onChange={(event) => setDescriptionExtraColumn(event.target.value)}>
                    <option value="">Nenhuma</option>
                    {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </label>
              <label>
                Estrutura dos valores
                <select
                  value={amountLayout}
                  onChange={(event) => {
                    const value = event.target.value as "single" | "debit_credit";
                    setAmountLayout(value);
                    setAmountColumn("");
                    setDebitColumn("");
                    setCreditColumn("");
                  }}
                >
                  <option value="single">Uma coluna com valores</option>
                  <option value="debit_credit">Colunas separadas de debito e credito</option>
                </select>
              </label>

              {amountLayout === "single" ? (
                <>
                  <label>
                    Coluna de valor
                    <select value={amountColumn} onChange={(event) => setAmountColumn(event.target.value)}>
                      <option value="">Selecione</option>
                      {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                  </label>

                  <label>
                    Sinal que representa despesa
                    <select value={amountMode} onChange={(event) => setAmountMode(event.target.value as ImportAmountMode)}>
                      <option value="positive">Valores positivos</option>
                      <option value="negative">Valores negativos</option>
                    </select>
                  </label>
                </>
              ) : (
                <>
                  <label>
                    Coluna de debito
                    <select value={debitColumn} onChange={(event) => setDebitColumn(event.target.value)}>
                      <option value="">Selecione</option>
                      {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                  </label>

                  <label>
                    Coluna de credito ou estorno
                    <select value={creditColumn} onChange={(event) => setCreditColumn(event.target.value)}>
                      <option value="">Nao existe</option>
                      {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                    </select>
                  </label>
                </>
              )}

                <label>
                  Identificador opcional
                  <select value={externalIdColumn} onChange={(event) => setExternalIdColumn(event.target.value)}>
                    <option value="">Nenhum</option>
                    {columnOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                  </select>
                </label>
                <label>
                  Formato da data
                  <select value={dateFormat} onChange={(event) => setDateFormat(event.target.value as ImportDateFormat)}>
                    <option value="auto">Detectar automaticamente</option>
                    <option value="dmy">Dia / mes / ano</option>
                    <option value="mdy">Mes / dia / ano</option>
                    <option value="ymd">Ano / mes / dia</option>
                  </select>
                </label>
                <label>
                  Separador decimal
                  <select value={decimalSeparator} onChange={(event) => setDecimalSeparator(event.target.value as ImportDecimalSeparator)}>
                    <option value="auto">Detectar automaticamente</option>
                    <option value="comma">Virgula</option>
                    <option value="dot">Ponto</option>
                  </select>
                </label>
              </div>

              <div className="raw-preview table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Linha</th>
                      {columnOptions.map((option) => <th key={option.value}>C{Number(option.value) + 1}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {inspection.rows.map((row, rowIndex) => (
                      <tr className={headerRow === rowIndex + 1 ? "mapped-header-row" : undefined} key={`${rowIndex}-${row.join("|")}`}>
                        <td>{rowIndex + 1}</td>
                        {columnOptions.map((option) => <td key={option.value}>{row[Number(option.value)] || "-"}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <p className="muted-copy">OFX possui estrutura padronizada e nao precisa de mapeamento manual.</p>
          )}

          <button className="primary-button" disabled={loading} onClick={() => void handlePreview()} type="button">
            {loading ? "Analisando..." : "Pre-visualizar lancamentos"}
          </button>
        </section>
      ) : null}

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
            <strong>{preview.rows.filter((row) => row.status === "ignored").length}<span>Ignorados</span></strong>
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
                    <td><strong>{row.purchase_place || "Linha sem descricao"}</strong><small>{row.error_message}</small></td>
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
