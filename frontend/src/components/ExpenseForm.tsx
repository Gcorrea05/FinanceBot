
import { useMemo, useState, type FormEvent } from "react";

import type {
  Expense,
  ExpenseMutationPayload,
  SharedPersonInput,
} from "../api/types";

interface ExpenseFormProps {
  expense?: Expense | null;
  categories: string[];
  paymentMethods: string[];
  busy?: boolean;
  onCancel: () => void;
  onSubmit: (payload: ExpenseMutationPayload) => Promise<void> | void;
}

interface ParticipantRow {
  id: number;
  name: string;
  amount: string;
}

function localDateTime(value?: string): string {
  const date = value ? new Date(value) : new Date();

  if (Number.isNaN(date.getTime())) {
    return value?.slice(0, 16) ?? "";
  }

  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

function normalizeName(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase();
}

function initialParticipants(expense?: Expense | null): ParticipantRow[] {
  if (!expense?.shared_people.length) {
    return [{ id: 1, name: "", amount: "" }];
  }

  return expense.shared_people.map((person, index) => ({
    id: index + 1,
    name: person.person_name,
    amount: person.amount,
  }));
}

export function ExpenseForm({
  expense,
  categories,
  paymentMethods,
  busy = false,
  onCancel,
  onSubmit,
}: ExpenseFormProps) {
  const firstInstallment = expense?.installments[0];
  const [purchaseDate, setPurchaseDate] = useState(
    localDateTime(expense?.purchase_date),
  );
  const [purchasePlace, setPurchasePlace] = useState(
    expense?.purchase_place ?? "",
  );
  const [purchaseValue, setPurchaseValue] = useState(
    expense?.purchase_value ?? "",
  );
  const [category, setCategory] = useState(
    expense?.category ?? categories[0] ?? "",
  );
  const [paymentMethod, setPaymentMethod] = useState(
    expense?.payment_method ?? paymentMethods[0] ?? "",
  );
  const [isInstallment, setIsInstallment] = useState(
    expense?.is_installment ?? false,
  );
  const [installments, setInstallments] = useState(
    firstInstallment?.total_installments ?? 2,
  );
  const [firstDueDate, setFirstDueDate] = useState(
    firstInstallment?.due_date ?? "",
  );
  const [isShared, setIsShared] = useState(expense?.is_shared ?? false);
  const [participants, setParticipants] = useState<ParticipantRow[]>(
    initialParticipants(expense),
  );
  const [notes, setNotes] = useState(expense?.notes ?? "");
  const [formError, setFormError] = useState<string | null>(null);

  const title = expense ? "Editar despesa" : "Nova despesa";
  const hasExactAmounts = useMemo(
    () => participants.some((participant) => participant.amount.trim()),
    [participants],
  );

  function updateParticipant(
    id: number,
    field: "name" | "amount",
    value: string,
  ) {
    setParticipants((current) =>
      current.map((participant) =>
        participant.id === id
          ? { ...participant, [field]: value }
          : participant,
      ),
    );
  }

  function addParticipant() {
    setParticipants((current) => [
      ...current,
      {
        id: Math.max(0, ...current.map((item) => item.id)) + 1,
        name: "",
        amount: "",
      },
    ]);
  }

  function removeParticipant(id: number) {
    setParticipants((current) => {
      const filtered = current.filter((participant) => participant.id !== id);
      return filtered.length ? filtered : [{ id: id + 1, name: "", amount: "" }];
    });
  }

  function validateParticipants(): SharedPersonInput[] {
    if (!isShared) {
      return [];
    }

    const completed = participants.map((participant) => ({
      name: participant.name.trim(),
      amount: participant.amount.trim(),
    }));

    if (completed.some((participant) => participant.name.length < 2)) {
      throw new Error("Informe o nome de todas as pessoas da divisao.");
    }

    const normalizedNames = completed.map((participant) =>
      normalizeName(participant.name),
    );

    if (new Set(normalizedNames).size !== normalizedNames.length) {
      throw new Error("A mesma pessoa nao pode ser adicionada duas vezes.");
    }

    const amountsFilled = completed.map((participant) => Boolean(participant.amount));

    if (amountsFilled.some(Boolean) && !amountsFilled.every(Boolean)) {
      throw new Error(
        "Preencha o valor de todas as pessoas ou deixe todos vazios para divisao igual.",
      );
    }

    if (amountsFilled.every(Boolean)) {
      const sharedTotal = completed.reduce(
        (total, participant) => total + Number(participant.amount.replace(",", ".")),
        0,
      );

      if (completed.some((participant) => Number(participant.amount.replace(",", ".")) <= 0)) {
        throw new Error("Os valores compartilhados devem ser maiores que zero.");
      }

      if (sharedTotal > Number(purchaseValue.replace(",", "."))) {
        throw new Error("A soma das partes nao pode superar o valor da despesa.");
      }
    }

    return completed.map((participant) => ({
      name: participant.name,
      amount: participant.amount
        ? participant.amount.replace(",", ".")
        : null,
    }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    try {
      if (purchasePlace.trim().length < 2) {
        throw new Error("Informe o estabelecimento.");
      }

      const normalizedValue = purchaseValue.replace(",", ".");

      if (!normalizedValue || Number(normalizedValue) <= 0) {
        throw new Error("Informe um valor maior que zero.");
      }

      if (!category || !paymentMethod) {
        throw new Error("Categoria e forma de pagamento sao obrigatorias.");
      }

      if (isInstallment && (installments < 1 || !firstDueDate)) {
        throw new Error("Informe ao menos 1 parcela e o primeiro vencimento.");
      }

      const sharedPeople = validateParticipants();
      const normalizedDate = purchaseDate.length === 16
        ? `${purchaseDate}:00`
        : purchaseDate;

      await onSubmit({
        purchase_date: normalizedDate,
        purchase_place: purchasePlace.trim(),
        purchase_value: normalizedValue,
        category,
        payment_method: paymentMethod,
        is_installment: isInstallment,
        installments: isInstallment ? installments : 1,
        first_installment_due_date: isInstallment ? firstDueDate : null,
        is_shared: isShared,
        shared_people: sharedPeople,
        notes: notes.trim() || null,
      });
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Nao foi possivel salvar a despesa.",
      );
    }
  }

  return (
    <div className="modal-backdrop" role="presentation">
      <section
        aria-labelledby="expense-form-title"
        aria-modal="true"
        className="modal-card expense-modal"
        role="dialog"
      >
        <div className="modal-header">
          <div>
            <span className="eyebrow">Lancamento</span>
            <h2 id="expense-form-title">{title}</h2>
          </div>
          <button
            aria-label="Fechar formulario"
            className="icon-button"
            onClick={onCancel}
            type="button"
          >
            X
          </button>
        </div>

        <form className="expense-form" onSubmit={(event) => void submit(event)}>
          {formError ? <div className="inline-alert error">{formError}</div> : null}

          <div className="form-grid two-columns">
            <label>
              Data e hora
              <input
                required
                type="datetime-local"
                value={purchaseDate}
                onChange={(event) => setPurchaseDate(event.target.value)}
              />
            </label>
            <label>
              Valor
              <input
                inputMode="decimal"
                placeholder="0,00"
                required
                value={purchaseValue}
                onChange={(event) => setPurchaseValue(event.target.value)}
              />
            </label>
          </div>

          <label>
            Estabelecimento
            <input
              maxLength={255}
              required
              value={purchasePlace}
              onChange={(event) => setPurchasePlace(event.target.value)}
            />
          </label>

          <div className="form-grid two-columns">
            <label>
              Categoria
              <select
                required
                value={category}
                onChange={(event) => setCategory(event.target.value)}
              >
                {categories.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              Forma de pagamento
              <select
                required
                value={paymentMethod}
                onChange={(event) => setPaymentMethod(event.target.value)}
              >
                {paymentMethods.map((item) => (
                  <option key={item} value={item}>{item}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="choice-panel">
            <label className="checkbox-row">
              <input
                checked={isInstallment}
                type="checkbox"
                onChange={(event) => setIsInstallment(event.target.checked)}
              />
              Compra parcelada
            </label>

            {isInstallment ? (
              <div className="form-grid two-columns nested-fields">
                <label>
                  Quantidade de parcelas
                  <input
                    max={120}
                    min={1}
                    type="number"
                    value={installments}
                    onChange={(event) => setInstallments(Number(event.target.value))}
                  />
                </label>
                <label>
                  Primeiro vencimento
                  <input
                    required
                    type="date"
                    value={firstDueDate}
                    onChange={(event) => setFirstDueDate(event.target.value)}
                  />
                </label>
              </div>
            ) : null}
          </div>

          <div className="choice-panel">
            <label className="checkbox-row">
              <input
                checked={isShared}
                type="checkbox"
                onChange={(event) => setIsShared(event.target.checked)}
              />
              Despesa compartilhada
            </label>

            {isShared ? (
              <div className="participant-editor nested-fields">
                <p>
                  Adicione uma pessoa por linha. Deixe os valores vazios para divisao igual.
                </p>
                {participants.map((participant) => (
                  <div className="participant-row" key={participant.id}>
                    <label>
                      Pessoa
                      <input
                        value={participant.name}
                        onChange={(event) =>
                          updateParticipant(participant.id, "name", event.target.value)
                        }
                      />
                    </label>
                    <label>
                      Valor {hasExactAmounts ? "devido" : "opcional"}
                      <input
                        inputMode="decimal"
                        placeholder="Divisao igual"
                        value={participant.amount}
                        onChange={(event) =>
                          updateParticipant(participant.id, "amount", event.target.value)
                        }
                      />
                    </label>
                    <button
                      className="danger-button compact"
                      onClick={() => removeParticipant(participant.id)}
                      type="button"
                    >
                      Remover
                    </button>
                  </div>
                ))}
                <button
                  className="secondary-button compact"
                  onClick={addParticipant}
                  type="button"
                >
                  Adicionar pessoa
                </button>
              </div>
            ) : null}
          </div>

          <label>
            Observacao
            <textarea
              maxLength={500}
              rows={3}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
            />
          </label>

          <div className="modal-actions">
            <button className="secondary-button" onClick={onCancel} type="button">
              Cancelar
            </button>
            <button className="primary-button" disabled={busy} type="submit">
              {busy ? "Salvando..." : "Salvar despesa"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
