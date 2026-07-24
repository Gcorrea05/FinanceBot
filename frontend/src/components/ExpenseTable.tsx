import type { Expense } from "../api/types";
import { formatCurrency, formatDate } from "../utils/formatters";

interface ExpenseTableProps {
  expenses: Expense[];
  onEdit?: (expense: Expense) => void;
  onDelete?: (expense: Expense) => void;
}

export function ExpenseTable({ expenses, onEdit, onDelete }: ExpenseTableProps) {
  const showActions = Boolean(onEdit || onDelete);

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Estabelecimento</th>
            <th>Categoria</th>
            <th>Pagamento</th>
            <th className="align-right">Valor</th>
            {showActions ? <th className="align-right">Acoes</th> : null}
          </tr>
        </thead>
        <tbody>
          {expenses.map((expense) => (
            <tr key={expense.id}>
              <td>{formatDate(expense.purchase_date)}</td>
              <td>
                <strong>{expense.purchase_place}</strong>
                <span className="row-note">
                  {expense.is_shared ? "Compartilhada" : "Individual"}
                  {expense.is_installment ? " | Parcelada" : ""}
                </span>
              </td>
              <td>{expense.category}</td>
              <td>{expense.payment_method}</td>
              <td className="align-right strong-cell">
                {formatCurrency(expense.purchase_value)}
              </td>
              {showActions ? (
                <td className="align-right">
                  <div className="table-actions">
                    {onEdit ? (
                      <button
                        className="secondary-button compact"
                        onClick={() => onEdit(expense)}
                        type="button"
                      >
                        Editar
                      </button>
                    ) : null}
                    {onDelete ? (
                      <button
                        className="danger-button compact"
                        onClick={() => onDelete(expense)}
                        type="button"
                      >
                        Excluir
                      </button>
                    ) : null}
                  </div>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
