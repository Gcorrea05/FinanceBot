import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";

import {
  financeApi,
} from "../api/client";
import type {
  ReferenceItem,
  ReportOverview,
  ReportQuery,
} from "../api/types";
import {
  BreakdownBars,
} from "../components/BreakdownBars";
import {
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import {
  MetricCard,
} from "../components/MetricCard";
import {
  TrendChart,
} from "../components/TrendChart";
import {
  formatCurrency,
  formatDate,
} from "../utils/formatters";
import "./reports.css";


interface PeriodValue {
  year: number;
  month: number;
}


function shiftMonth(
  source: Date,
  amount: number,
): PeriodValue {
  const result = new Date(
    source.getFullYear(),
    source.getMonth() + amount,
    1,
  );

  return {
    year: result.getFullYear(),
    month: result.getMonth() + 1,
  };
}


export function ReportsPage() {
  const now = useMemo(
    () => new Date(),
    [],
  );

  const initialStart = useMemo(
    () => shiftMonth(
      now,
      -5,
    ),
    [now],
  );

  const [startYear, setStartYear] =
    useState(
      initialStart.year
    );

  const [startMonth, setStartMonth] =
    useState(
      initialStart.month
    );

  const [endYear, setEndYear] =
    useState(
      now.getFullYear()
    );

  const [endMonth, setEndMonth] =
    useState(
      now.getMonth() + 1
    );

  const [category, setCategory] =
    useState("");

  const [
    paymentMethod,
    setPaymentMethod,
  ] = useState("");

  const [place, setPlace] =
    useState("");

  const [categories, setCategories] =
    useState<ReferenceItem[]>([]);

  const [
    paymentMethods,
    setPaymentMethods,
  ] = useState<ReferenceItem[]>([]);

  const [report, setReport] =
    useState<ReportOverview | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);

  const [exporting, setExporting] =
    useState(false);

  const [error, setError] =
    useState<string | null>(
      null
    );

  const query = useCallback(
    (): ReportQuery => ({
      start_year: startYear,
      start_month: startMonth,
      end_year: endYear,
      end_month: endMonth,
      category: (
        category || undefined
      ),
      payment_method: (
        paymentMethod || undefined
      ),
      place: (
        place.trim() || undefined
      ),
    }),
    [
      category,
      endMonth,
      endYear,
      paymentMethod,
      place,
      startMonth,
      startYear,
    ],
  );

  const load = useCallback(
    async () => {
      setLoading(true);
      setError(null);

      try {
        const [
          reportResponse,
          categoriesResponse,
          paymentResponse,
        ] = await Promise.all([
          financeApi.getReport(
            query()
          ),
          financeApi.listCategories(),
          financeApi.listPaymentMethods(),
        ]);

        setReport(
          reportResponse
        );
        setCategories(
          categoriesResponse.items
        );
        setPaymentMethods(
          paymentResponse.items
        );
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : "Nao foi possivel carregar os relatorios.",
        );
      } finally {
        setLoading(false);
      }
    },
    [query],
  );

  useEffect(() => {
    void load();
  }, [load]);

  function submit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    void load();
  }


  async function exportMonthlyExcel() {
    setExporting(true);
    setError(null);

    try {
      const blob = await financeApi.downloadMonthlyExcel(
        endYear,
        endMonth,
      );
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `financebot_relatorio_${endYear}_${String(endMonth).padStart(2, "0")}.xlsx`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (exportError) {
      setError(
        exportError instanceof Error
          ? exportError.message
          : "Nao foi possivel exportar o Excel.",
      );
    } finally {
      setExporting(false);
    }
  }

  function clearFilters() {
    const start = shiftMonth(
      now,
      -5,
    );

    setStartYear(
      start.year
    );
    setStartMonth(
      start.month
    );
    setEndYear(
      now.getFullYear()
    );
    setEndMonth(
      now.getMonth() + 1
    );
    setCategory("");
    setPaymentMethod("");
    setPlace("");
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">
            Analise financeira
          </span>
          <h1>Relatorios</h1>
          <p>
            Compare meses, categorias, estabelecimentos e compromissos parcelados.
          </p>
        </div>
      </header>

      <section className="panel report-filter-panel">
        <form
          className="report-filter-form"
          onSubmit={submit}
        >
          <fieldset>
            <legend>Periodo inicial</legend>

            <label>
              Mes
              <select
                value={startMonth}
                onChange={(event) =>
                  setStartMonth(
                    Number(
                      event.target.value
                    )
                  )
                }
              >
                {Array.from(
                  {
                    length: 12,
                  },
                  (_, index) =>
                    index + 1,
                ).map((value) => (
                  <option
                    key={value}
                    value={value}
                  >
                    {String(value).padStart(
                      2,
                      "0",
                    )}
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
                value={startYear}
                onChange={(event) =>
                  setStartYear(
                    Number(
                      event.target.value
                    )
                  )
                }
              />
            </label>
          </fieldset>

          <fieldset>
            <legend>Periodo final</legend>

            <label>
              Mes
              <select
                value={endMonth}
                onChange={(event) =>
                  setEndMonth(
                    Number(
                      event.target.value
                    )
                  )
                }
              >
                {Array.from(
                  {
                    length: 12,
                  },
                  (_, index) =>
                    index + 1,
                ).map((value) => (
                  <option
                    key={value}
                    value={value}
                  >
                    {String(value).padStart(
                      2,
                      "0",
                    )}
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
                value={endYear}
                onChange={(event) =>
                  setEndYear(
                    Number(
                      event.target.value
                    )
                  )
                }
              />
            </label>
          </fieldset>

          <label>
            Categoria
            <select
              value={category}
              onChange={(event) =>
                setCategory(
                  event.target.value
                )
              }
            >
              <option value="">
                Todas
              </option>

              {categories.map((item) => (
                <option
                  key={item.name}
                  value={item.name}
                >
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Pagamento
            <select
              value={paymentMethod}
              onChange={(event) =>
                setPaymentMethod(
                  event.target.value
                )
              }
            >
              <option value="">
                Todos
              </option>

              {paymentMethods.map(
                (item) => (
                  <option
                    key={item.name}
                    value={item.name}
                  >
                    {item.name}
                  </option>
                )
              )}
            </select>
          </label>

          <label className="place-filter">
            Estabelecimento
            <input
              maxLength={255}
              value={place}
              onChange={(event) =>
                setPlace(
                  event.target.value
                )
              }
              placeholder="Parte do nome"
            />
          </label>

          <div className="report-filter-actions">
            <button
              className="secondary-button"
              onClick={clearFilters}
              type="button"
            >
              Limpar
            </button>

            <button
              className="secondary-button"
              disabled={exporting}
              onClick={() => void exportMonthlyExcel()}
              type="button"
            >
              {exporting
                ? "Gerando Excel..."
                : `Exportar ${String(endMonth).padStart(2, "0")}/${endYear}`}
            </button>

            <button
              className="primary-button"
              type="submit"
            >
              Gerar relatorio
            </button>
          </div>
        </form>
      </section>

      {error ? (
        <ErrorState
          title="Falha nos relatorios"
          message={error}
          onRetry={() => void load()}
        />
      ) : loading || !report ? (
        <LoadingState
          message="Calculando relatorios..."
        />
      ) : (
        <>
          <section className="metric-grid report-metrics">
            <MetricCard
              label="Total no periodo"
              value={formatCurrency(
                report.total_spent
              )}
              helper={`${report.transactions} compra(s) considerada(s)`}
            />

            <MetricCard
              label="Media mensal"
              value={formatCurrency(
                report.monthly_average
              )}
              helper={`${report.monthly.length} mes(es) comparados`}
            />

            <MetricCard
              label="Maior mes"
              value={
                report.highest_month
                  ? formatCurrency(
                      report.highest_month.total
                    )
                  : "-"
              }
              helper={
                report.highest_month
                  ? report.highest_month.label
                  : "Sem movimento"
              }
            />

            <MetricCard
              label="Parcelas pendentes"
              value={formatCurrency(
                report.installment_commitment
              )}
              helper={`${report.installments.length} compra(s) ativa(s)`}
            />
          </section>

          <section className="panel report-section">
            <div className="section-heading">
              <div>
                <span className="eyebrow">
                  Comparacao mensal
                </span>
                <h2>Evolucao dos gastos</h2>
              </div>
            </div>

            <TrendChart
              items={report.monthly}
            />
          </section>

          <div className="report-grid">
            <section className="panel report-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">
                    Distribuicao
                  </span>
                  <h2>Gastos por categoria</h2>
                </div>
              </div>

              <BreakdownBars
                items={report.categories}
              />
            </section>

            <section className="panel report-section">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">
                    Ranking
                  </span>
                  <h2>Estabelecimentos</h2>
                </div>
              </div>

              {report.merchants.length === 0 ? (
                <p className="empty-copy">
                  Nenhum estabelecimento encontrado.
                </p>
              ) : (
                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Estabelecimento</th>
                        <th>Compras</th>
                        <th className="align-right">
                          Sua parte
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.merchants.map(
                        (item) => (
                          <tr key={item.name}>
                            <td className="strong-cell">
                              {item.name}
                            </td>
                            <td>
                              {item.transactions}
                            </td>
                            <td className="align-right strong-cell">
                              {formatCurrency(
                                item.total
                              )}
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>

          <section className="panel report-section">
            <div className="section-heading">
              <div>
                <span className="eyebrow">
                  Compromissos futuros
                </span>
                <h2>Parcelamentos ativos</h2>
              </div>
            </div>

            {report.installments.length === 0 ? (
              <p className="empty-copy">
                Nenhum parcelamento ativo encontrado para os filtros.
              </p>
            ) : (
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Compra</th>
                      <th>Categoria</th>
                      <th>Progresso</th>
                      <th>Proximo vencimento</th>
                      <th className="align-right">
                        Restante
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.installments.map(
                      (item) => (
                        <tr key={item.expense_id}>
                          <td>
                            <strong>
                              {item.purchase_place}
                            </strong>
                            <span className="row-note">
                              {item.payment_method}
                              {" - "}
                              Sua parte:{" "}
                              {formatCurrency(
                                item.owner_total
                              )}
                            </span>
                          </td>
                          <td>{item.category}</td>
                          <td>
                            {item.paid_installments}
                            /
                            {item.total_installments}
                            {" pagas"}
                          </td>
                          <td>
                            {item.next_due_date
                              ? formatDate(
                                  `${item.next_due_date}T12:00:00`
                                )
                              : "-"}
                          </td>
                          <td className="align-right strong-cell">
                            {formatCurrency(
                              item.remaining_amount
                            )}
                          </td>
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
