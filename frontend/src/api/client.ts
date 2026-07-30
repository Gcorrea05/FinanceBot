import type {
  AutomationHistoryResponse,
  AutomationPreviewResponse,
  AutomationRunResponse,
  AutomationSettings,
  AutomationSettingsPayload,
  BudgetOverview,
  BudgetPlanPayload,
  DashboardOverview,
  Expense,
  ExpenseListResponse,
  ExpenseMutationPayload,
  ExpenseQuery,
  FutureOverview,
  RecurringExpense,
  RecurringExpensePayload,
  HealthResponse,
  ImportBatch,
  ImportColumnMapping,
  ImportHistoryResponse,
  ImportInspection,
  IntelligenceOverview,
  IntelligenceQuery,
  ReceivableDetailResponse,
  ReceivableHistoryResponse,
  ReceivableSettlementResponse,
  ReceivableSummaryResponse,
  ReferenceListResponse,
  ReportOverview,
  ReportQuery,
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

async function download(path: string): Promise<Blob> {
  let response: Response;

  try {
    response = await fetch(`${resolveApiUrl()}${path}`, {
      headers: {
        Accept: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
    throw new ApiError(
      `A API retornou o status ${response.status}.`,
      response.status,
    );
  }

  return response.blob();
}

function buildQuery(params: object): string {
  const search = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (
      value !== undefined
      && value !== null
      && value !== ""
    ) {
      search.set(key, String(value));
    }
  });

  const query = search.toString();
  return query ? `?${query}` : "";
}

function jsonRequest<TPayload, TResponse>(
  path: string,
  method: "POST" | "PUT",
  payload: TPayload,
): Promise<TResponse> {
  return request<TResponse>(path, {
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
    return jsonRequest<ExpenseMutationPayload, Expense>(
      "/expenses",
      "POST",
      payload,
    );
  },

  updateExpense(
    expenseId: number,
    payload: ExpenseMutationPayload,
  ): Promise<Expense> {
    return jsonRequest<ExpenseMutationPayload, Expense>(
      `/expenses/${expenseId}`,
      "PUT",
      payload,
    );
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

  listSettledReceivables(): Promise<ReceivableHistoryResponse> {
    return request<ReceivableHistoryResponse>(
      "/receivables/settled",
    );
  },

  reopenReceivable(receivableId: number): Promise<ReceivableSettlementResponse> {
    return request<ReceivableSettlementResponse>(
      `/receivables/${receivableId}/reopen`,
      { method: "POST" },
    );
  },

  getBudget(year: number, month: number): Promise<BudgetOverview> {
    return request<BudgetOverview>(`/budgets/${year}/${month}`);
  },

  saveBudget(
    year: number,
    month: number,
    payload: BudgetPlanPayload,
  ): Promise<BudgetOverview> {
    return jsonRequest<BudgetPlanPayload, BudgetOverview>(
      `/budgets/${year}/${month}`,
      "PUT",
      payload,
    );
  },

  getReport(
    params: ReportQuery,
  ): Promise<ReportOverview> {
    return request<ReportOverview>(
      `/reports/overview${buildQuery(params)}`,
    );
  },

  downloadMonthlyExcel(
    year: number,
    month: number,
  ): Promise<Blob> {
    return download(
      `/exports/monthly.xlsx?year=${year}&month=${month}`,
    );
  },

  inspectImport(
    file: File,
    sheetName?: string,
  ): Promise<ImportInspection> {
    const form = new FormData();
    form.append("file", file);
    if (sheetName) {
      form.append("sheet_name", sheetName);
    }
    return request<ImportInspection>("/imports/inspect", {
      method: "POST",
      body: form,
    });
  },

  previewImport(
    file: File,
    defaultCategory: string,
    defaultPaymentMethod: string,
    mapping?: ImportColumnMapping,
  ): Promise<ImportBatch> {
    const form = new FormData();
    form.append("file", file);
    form.append("default_category", defaultCategory);
    form.append("default_payment_method", defaultPaymentMethod);
    if (mapping) {
      form.append("mapping_json", JSON.stringify(mapping));
    }
    return request<ImportBatch>("/imports/preview", {
      method: "POST",
      body: form,
    });
  },

  confirmImport(batchId: number): Promise<ImportBatch> {
    return request<ImportBatch>(`/imports/${batchId}/confirm`, { method: "POST" });
  },

  listImports(): Promise<ImportHistoryResponse> {
    return request<ImportHistoryResponse>("/imports");
  },

  getImport(batchId: number): Promise<ImportBatch> {
    return request<ImportBatch>(`/imports/${batchId}`);
  },

  getIntelligenceOverview(
    query: IntelligenceQuery,
  ): Promise<IntelligenceOverview> {
    const parameters = new URLSearchParams({
      year: String(query.year),
      month: String(query.month),
    });
    return request<IntelligenceOverview>(
      `/intelligence/overview?${parameters.toString()}`,
    );
  },

  getAutomationSettings(): Promise<AutomationSettings> {
    return request<AutomationSettings>("/automations/settings");
  },

  saveAutomationSettings(
    payload: AutomationSettingsPayload,
  ): Promise<AutomationSettings> {
    return jsonRequest<AutomationSettingsPayload, AutomationSettings>(
      "/automations/settings",
      "PUT",
      payload,
    );
  },

  disconnectTelegram(): Promise<AutomationSettings> {
    return request<AutomationSettings>(
      "/automations/disconnect",
      { method: "POST" },
    );
  },

  previewAutomations(): Promise<AutomationPreviewResponse> {
    return request<AutomationPreviewResponse>("/automations/preview");
  },

  runAutomationsNow(): Promise<AutomationRunResponse> {
    return request<AutomationRunResponse>(
      "/automations/run",
      { method: "POST" },
    );
  },

  getDashboard(
    year: number,
    month: number,
  ): Promise<DashboardOverview> {
    return request<DashboardOverview>(
      `/dashboard/overview?year=${year}&month=${month}`,
    );
  },

  getFutureOverview(
    fromYear: number,
    fromMonth: number,
    months = 12,
  ): Promise<FutureOverview> {
    return request<FutureOverview>(
      `/future/overview?from_year=${fromYear}&from_month=${fromMonth}&months=${months}`,
    );
  },

  listRecurringExpenses(): Promise<RecurringExpense[]> {
    return request<RecurringExpense[]>("/recurring-expenses");
  },

  updateRecurringExpense(
    recurringId: number,
    payload: RecurringExpensePayload,
  ): Promise<RecurringExpense> {
    return jsonRequest<RecurringExpensePayload, RecurringExpense>(
      `/recurring-expenses/${recurringId}`,
      "PUT",
      payload,
    );
  },

  listAutomationDeliveries(): Promise<AutomationHistoryResponse> {
    return request<AutomationHistoryResponse>(
      "/automations/deliveries",
    );
  },
};
