export interface HealthResponse {
  status: string;
}

export interface Installment {
  id: number;
  installment_number: number;
  total_installments: number;
  due_date: string;
  amount: string;
  is_paid: boolean;
  paid_at: string | null;
}

export interface SharedPerson {
  receivable_id: number;
  person_id: number;
  person_name: string;
  amount: string;
  is_settled: boolean;
  settled_at: string | null;
}

export interface Expense {
  id: number;
  purchase_date: string;
  purchase_place: string;
  purchase_value: string;
  category: string;
  payment_method: string;
  is_installment: boolean;
  is_shared: boolean;
  owner_amount: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  installments: Installment[];
  shared_people: SharedPerson[];
}

export interface ExpenseListResponse {
  items: Expense[];
  total: number;
  limit: number;
  offset: number;
}

export interface ReferenceItem {
  name: string;
}

export interface ReferenceListResponse {
  items: ReferenceItem[];
}

export interface SharedPersonInput {
  name: string;
  amount: string | null;
}

export interface ExpenseMutationPayload {
  purchase_date: string;
  purchase_place: string;
  purchase_value: string;
  category: string;
  payment_method: string;
  is_installment: boolean;
  installments: number;
  first_installment_due_date: string | null;
  is_shared: boolean;
  shared_people: SharedPersonInput[];
  notes: string | null;
}

export interface ReceivablePersonSummary {
  person_id: number;
  person_name: string;
  total: string;
  pending_count: number;
}

export interface ReceivableSummaryResponse {
  people: ReceivablePersonSummary[];
  total_general: string;
}

export interface ReceivableItem {
  receivable_id: number;
  expense_id: number;
  person_id: number;
  person_name: string;
  purchase_place: string;
  purchase_date: string;
  amount: string;
}

export interface ReceivableDetailResponse {
  person_id: number;
  person_name: string;
  items: ReceivableItem[];
  total: string;
}

export interface ReceivableSettlementResponse {
  receivable_id: number;
  is_settled: boolean;
  settled_at: string;
}

export interface ExpenseQuery {
  limit?: number;
  offset?: number;
  month?: number;
  year?: number;
}
