import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react";

import { financeApi } from "../api/client";
import type {
  BudgetOverview,
  BudgetPlanPayload,
} from "../api/types";
import {
  ErrorState,
  LoadingState,
} from "../components/Feedback";
import { MetricCard } from "../components/MetricCard";
import { formatCurrency } from "../utils/formatters";
import "./budget.css";


const STATUS_LABELS = {
  not_configured: "Nao configurado",
  healthy: "Dentro do plano",
  attention: "Atencao ao limite",
  exceeded: "Limite ultrapassado",
} as const;


export function BudgetPage() {
  const now = useMemo(
    () => new Date(),
    [],
  );

  const [month, setMonth] = useState(
    now.getMonth() + 1,
  );

  const [year, setYear] = useState(
    now.getFullYear(),
  );

  const [overview, setOverview] =
    useState<BudgetOverview | null>(
      null
    );

  const [monthlyIncome, setMonthlyIncome] =
    useState("");

  const [reserveTarget, setReserveTarget] =
    useState("0.00");

  const [spendingLimit, setSpendingLimit] =
    useState("");

  const [repeatMonths, setRepeatMonths] =
    useState(1);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState<string | null>(
      null
    );

  const [success, setSuccess] =
    useState<string | null>(
      null
    );

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await financeApi.getBudget(
        year,
        month,
      );

      setOverview(result);

      if (result.configured) {
        setMonthlyIncome(
          result.monthly_income ?? ""
        );

        setReserveTarget(
          result.reserve_target ?? "0.00"
        );

        setSpendingLimit(
          result.spending_limit ?? ""
        );
      } else {
        setMonthlyIncome("");
        setReserveTarget("0.00");
        setSpendingLimit("");
      }
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel carregar o planejamento.",
      );
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const payload: BudgetPlanPayload = {
      monthly_income: monthlyIncome,
      reserve_target: reserveTarget,
      spending_limit: spendingLimit,
      repeat_months: repeatMonths,
    };

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await financeApi.saveBudget(
        year,
        month,
        payload,
      );

      setOverview(result);
      setSuccess(
        repeatMonths > 1
          ? `Planejamento salvo por ${repeatMonths} meses.`
          : "Planejamento mensal salvo com sucesso."
      );
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Nao foi possivel salvar o planejamento.",
      );
    } finally {
      setSaving(false);
    }
  }

  function applyPeriod(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    void load();
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">
            Controle mensal
          </span>
          <h1>Planejamento</h1>
          <p>
            Defina renda, reserva e limite de gastos para o periodo.
          </p>
        </div>

        {overview ? (
          <span
            className={`budget-status ${overview.status}`}
          >
            {STATUS_LABELS[overview.status]}
          </span>
        ) : null}
      </header>

      <section className="panel filter-panel">
        <form
          className="filter-form"
          onSubmit={applyPeriod}
        >
          <label>
            Mes
            <select
              value={month}
              onChange={(event) =>
                setMonth(
                  Number(event.target.value)
                )
              }
            >
              {Array.from(
                { length: 12 },
                (_, index) => index + 1,
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
              value={year}
              onChange={(event) =>
                setYear(
                  Number(event.target.value)
                )
              }
            />
          </label>

          <button
            className="secondary-button"
            type="submit"
          >
            Carregar periodo
          </button>
        </form>
      </section>

      {error ? (
        <ErrorState
          title="Falha no planejamento"
          message={error}
          onRetry={() => void load()}
        />
      ) : loading || !overview ? (
        <LoadingState
          message="Carregando planejamento..."
        />
      ) : (
        <>
          {success ? (
            <div className="inline-alert success">
              {success}
            </div>
          ) : null}

          <section className="metric-grid budget-metrics">
            <MetricCard
              label="Gasto considerado"
              value={formatCurrency(
                overview.spent
              )}
              helper="Sua parte nas despesas e parcelas do mes"
            />

            <MetricCard
              label="Limite restante"
              value={
                overview.remaining !== null
                  ? formatCurrency(
                      overview.remaining
                    )
                  : "-"
              }
              helper={
                overview.configured
                  ? `${overview.usage_percent ?? "0.00"}% do limite utilizado`
                  : "Configure o planejamento abaixo"
              }
            />

            <MetricCard
              label="Limite diario"
              value={
                overview.daily_limit !== null
                  ? formatCurrency(
                      overview.daily_limit
                    )
                  : "-"
              }
              helper={`${overview.remaining_days} dia(s) restante(s) no periodo`}
            />

            <MetricCard
              label="Disponivel apos reserva"
              value={
                overview.available_after_reserve !== null
                  ? formatCurrency(
                      overview.available_after_reserve
                    )
                  : "-"
              }
              helper="Renda menos reserva e gastos considerados"
            />
          </section>

          <div className="budget-layout">
            <section className="panel">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">
                    Plano do periodo
                  </span>
                  <h2>Valores mensais</h2>
                </div>
              </div>

              <form
                className="budget-form"
                onSubmit={save}
              >
                <label>
                  Renda mensal
                  <input
                    inputMode="decimal"
                    required
                    value={monthlyIncome}
                    onChange={(event) =>
                      setMonthlyIncome(
                        event.target.value
                      )
                    }
                    placeholder="5000,00"
                  />
                </label>

                <label>
                  Meta de reserva
                  <input
                    inputMode="decimal"
                    required
                    value={reserveTarget}
                    onChange={(event) =>
                      setReserveTarget(
                        event.target.value
                      )
                    }
                    placeholder="1000,00"
                  />
                </label>

                <label>
                  Limite de gastos
                  <input
                    inputMode="decimal"
                    required
                    value={spendingLimit}
                    onChange={(event) =>
                      setSpendingLimit(
                        event.target.value
                      )
                    }
                    placeholder="3500,00"
                  />
                </label>

                <label>
                  Aplicar a partir deste mes
                  <select
                    value={repeatMonths}
                    onChange={(event) => setRepeatMonths(Number(event.target.value))}
                  >
                    <option value={1}>Somente este mes</option>
                    <option value={3}>Este mes e os proximos 2</option>
                    <option value={6}>Este mes e os proximos 5</option>
                    <option value={12}>Este mes e os proximos 11</option>
                    <option value={24}>Este mes e os proximos 23</option>
                  </select>
                </label>

                <button
                  className="primary-button"
                  disabled={saving}
                  type="submit"
                >
                  {saving
                    ? "Salvando..."
                    : "Salvar planejamento"}
                </button>
              </form>
            </section>

            <section className="panel budget-rule-panel">
              <span className="eyebrow">
                Regra de calculo
              </span>
              <h2>O que entra no gasto mensal?</h2>

              <p>
                Despesas simples entram pela data da compra.
                Compras parceladas entram pelo vencimento de
                cada parcela.
              </p>

              <p>
                Em compras compartilhadas, apenas a sua parte
                compoe o planejamento. Valores que outras pessoas
                devem continuam na area de valores a receber.
              </p>

              <p>
                A soma do limite de gastos com a reserva nao pode
                ultrapassar a renda mensal informada.
              </p>
            </section>
          </div>
        </>
      )}
    </div>
  );
}
