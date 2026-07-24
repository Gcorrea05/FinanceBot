import type { Expense } from "../api/types";
import { formatCurrency, formatDate } from "../utils/formatters";

interface ExpenseTableProps {
  expenses: Expense[];
}

export function ExpenseTable({ expenses }: ExpenseTableProps) {
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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
