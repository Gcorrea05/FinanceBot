import type {
  Expense,
  ExpenseListResponse,
  ExpenseMutationPayload,
  ExpenseQuery,
  HealthResponse,
  ReceivableDetailResponse,
  ReceivableSettlementResponse,
  ReceivableSummaryResponse,
  ReferenceListResponse,
} from "./types";

const DEFAULT_API_URL = "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  readonly status: number;
  readonly details: unknown;

  constructor(message: string, status: number, details: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function resolveApiUrl(): string {
  const configured = import.meta.env.VITE_API_URL?.trim();
  return (configured || DEFAULT_API_URL).replace(/\/$/, "");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${resolveApiUrl()}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...init?.headers,
      },
    });
  } catch (error) {
    throw new ApiError(
      "Nao foi possivel conectar com a API do FinanceBot.",
      0,
      error,
    );
  }

  if (!response.ok) {
    let details: unknown = null;

    try {
      details = await response.json();
    } catch {
      details = await response.text();
    }

    const detailMessage =
      details && typeof details === "object" && "detail" in details
        ? String((details as { detail: unknown }).detail)
        : `A API retornou o status ${response.status}.`;

    throw new ApiError(detailMessage, response.status, details);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

function buildQuery(params: ExpenseQuery): string {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      search.set(key, String(value));
    }
  });

  const query = search.toString();
  return query ? `?${query}` : "";
}

function jsonRequest<T>(
  path: string,
  method: "POST" | "PUT",
  payload: ExpenseMutationPayload,
): Promise<T> {
  return request<T>(path, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}

export const financeApi = {
  live(): Promise<HealthResponse> {
    return request<HealthResponse>("/health/live");
  },

  ready(): Promise<HealthResponse> {
    return request<HealthResponse>("/health/ready");
  },

  listCategories(): Promise<ReferenceListResponse> {
    return request<ReferenceListResponse>("/references/categories");
  },

  listPaymentMethods(): Promise<ReferenceListResponse> {
    return request<ReferenceListResponse>("/references/payment-methods");
  },

  listExpenses(params: ExpenseQuery = {}): Promise<ExpenseListResponse> {
    return request<ExpenseListResponse>(`/expenses${buildQuery(params)}`);
  },

  getExpense(expenseId: number): Promise<Expense> {
    return request<Expense>(`/expenses/${expenseId}`);
  },

  createExpense(payload: ExpenseMutationPayload): Promise<Expense> {
    return jsonRequest<Expense>("/expenses", "POST", payload);
  },

  updateExpense(
    expenseId: number,
    payload: ExpenseMutationPayload,
  ): Promise<Expense> {
    return jsonRequest<Expense>(`/expenses/${expenseId}`, "PUT", payload);
  },

  deleteExpense(expenseId: number): Promise<void> {
    return request<void>(`/expenses/${expenseId}`, { method: "DELETE" });
  },

  listReceivables(): Promise<ReceivableSummaryResponse> {
    return request<ReceivableSummaryResponse>("/receivables");
  },

  listPersonReceivables(personId: number): Promise<ReceivableDetailResponse> {
    return request<ReceivableDetailResponse>(
      `/receivables/people/${personId}`,
    );
  },

  settleReceivable(receivableId: number): Promise<ReceivableSettlementResponse> {
    return request<ReceivableSettlementResponse>(
      `/receivables/${receivableId}/settle`,
      { method: "POST" },
    );
  },
};
