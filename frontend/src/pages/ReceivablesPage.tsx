import { useCallback, useEffect, useState } from "react";

import { financeApi } from "../api/client";
import type {
  ReceivableDetailResponse,
  ReceivableHistoryResponse,
  ReceivablePersonSummary,
  ReceivableSummaryResponse,
} from "../api/types";
import { EmptyState, ErrorState, LoadingState } from "../components/Feedback";
import { formatCurrency, formatDate } from "../utils/formatters";

export function ReceivablesPage() {
  const [summary, setSummary] = useState<ReceivableSummaryResponse | null>(null);
  const [history, setHistory] = useState<ReceivableHistoryResponse>({ items: [] });
  const [selectedPerson, setSelectedPerson] = useState<ReceivablePersonSummary | null>(null);
  const [details, setDetails] = useState<ReceivableDetailResponse | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    setError(null);

    try {
      const [summaryResponse, historyResponse] = await Promise.all([
        financeApi.listReceivables(),
        financeApi.listSettledReceivables(),
      ]);
      setSummary(summaryResponse);
      setHistory(historyResponse);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel carregar os valores a receber.",
      );
    }
  }, []);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  async function selectPerson(person: ReceivablePersonSummary) {
    setSelectedPerson(person);
    setLoadingDetails(true);
    setError(null);

    try {
      setDetails(await financeApi.listPersonReceivables(person.person_id));
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Nao foi possivel carregar as pendencias desta pessoa.",
      );
    } finally {
      setLoadingDetails(false);
    }
  }

  async function refreshSelectedPerson() {
    if (!selectedPerson) return;
    const refreshed = await financeApi.listPersonReceivables(selectedPerson.person_id);
    setDetails(refreshed);

    if (!refreshed.items.length) {
      setSelectedPerson(null);
      setDetails(null);
    }
  }

  async function settle(receivableId: number) {
    const confirmed = window.confirm("Confirmar que este valor foi recebido?");

    if (!confirmed) {
      return;
    }

    try {
      await financeApi.settleReceivable(receivableId);
      await loadSummary();
      await refreshSelectedPerson();
    } catch (settleError) {
      setError(
        settleError instanceof Error
          ? settleError.message
          : "Nao foi possivel registrar o recebimento.",
      );
    }
  }

  async function reopen(receivableId: number) {
    const confirmed = window.confirm(
      "Desfazer este recebimento e devolver o valor para as pendencias?",
    );

    if (!confirmed) return;

    try {
      await financeApi.reopenReceivable(receivableId);
      await loadSummary();
      await refreshSelectedPerson();
    } catch (reopenError) {
      setError(
        reopenError instanceof Error
          ? reopenError.message
          : "Nao foi possivel desfazer o recebimento.",
      );
    }
  }

  return (
    <div>
      <header className="page-header">
        <div>
          <span className="eyebrow">Compartilhamentos</span>
          <h1>Valores a receber</h1>
          <p>Consulte pendencias, registre recebimentos e corrija baixas feitas por engano.</p>
        </div>
        {summary ? (
          <div className="headline-total">
            <span>Total em aberto</span>
            <strong>{formatCurrency(summary.total_general)}</strong>
          </div>
        ) : null}
      </header>

      {error ? (
        <ErrorState title="Falha na consulta" message={error} onRetry={() => void loadSummary()} />
      ) : !summary ? (
        <LoadingState />
      ) : !summary.people.length ? (
        <EmptyState
          title="Nenhuma pendencia em aberto"
          message="Os valores compartilhados pendentes aparecerao aqui."
        />
      ) : (
        <div className="receivables-layout">
          <section className="panel people-panel">
            <div className="section-heading">
              <div>
                <span className="eyebrow">Pessoas</span>
                <h2>Resumo</h2>
              </div>
            </div>

            <div className="people-list">
              {summary.people.map((person) => (
                <button
                  className={
                    selectedPerson?.person_id === person.person_id
                      ? "person-row active"
                      : "person-row"
                  }
                  key={person.person_id}
                  onClick={() => void selectPerson(person)}
                  type="button"
                >
                  <span>
                    <strong>{person.person_name}</strong>
                    <small>{person.pending_count} pendencia(s)</small>
                  </span>
                  <strong>{formatCurrency(person.total)}</strong>
                </button>
              ))}
            </div>
          </section>

          <section className="panel detail-panel">
            {!selectedPerson ? (
              <EmptyState
                title="Selecione uma pessoa"
                message="Escolha um nome para visualizar as compras pendentes."
              />
            ) : loadingDetails ? (
              <LoadingState message="Carregando pendencias..." />
            ) : details ? (
              <>
                <div className="section-heading">
                  <div>
                    <span className="eyebrow">Detalhamento</span>
                    <h2>{details.person_name || selectedPerson.person_name}</h2>
                  </div>
                  <strong>{formatCurrency(details.total)}</strong>
                </div>

                <div className="receivable-items">
                  {details.items.map((item) => (
                    <article className="receivable-item" key={item.receivable_id}>
                      <div>
                        <strong>{item.purchase_place}</strong>
                        <span>{formatDate(item.purchase_date)}</span>
                      </div>
                      <div className="receivable-actions">
                        <strong>{formatCurrency(item.amount)}</strong>
                        <button
                          className="primary-button compact"
                          type="button"
                          onClick={() => void settle(item.receivable_id)}
                        >
                          Marcar recebido
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              </>
            ) : null}
          </section>
        </div>
      )}

      <section className="panel" style={{ marginTop: "1.5rem" }}>
        <div className="section-heading">
          <div>
            <span className="eyebrow">Historico recente</span>
            <h2>Valores marcados como recebidos</h2>
          </div>
        </div>

        {!history.items.length ? (
          <p className="empty-copy">Nenhum recebimento registrado recentemente.</p>
        ) : (
          <div className="receivable-items">
            {history.items.map((item) => (
              <article className="receivable-item" key={item.receivable_id}>
                <div>
                  <strong>{item.person_name} - {item.purchase_place}</strong>
                  <span>Recebido em {formatDate(item.settled_at)}</span>
                </div>
                <div className="receivable-actions">
                  <strong>{formatCurrency(item.amount)}</strong>
                  <button
                    className="secondary-button compact"
                    type="button"
                    onClick={() => void reopen(item.receivable_id)}
                  >
                    Desfazer recebimento
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
