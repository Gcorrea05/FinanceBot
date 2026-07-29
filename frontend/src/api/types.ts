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
  settled_at: string | null;
}

export interface SettledReceivableItem extends ReceivableItem {
  settled_at: string;
}

export interface ReceivableHistoryResponse {
  items: SettledReceivableItem[];
}

export interface ExpenseQuery {
  limit?: number;
  offset?: number;
  month?: number;
  year?: number;
}

export type BudgetStatus =
  | "not_configured"
  | "healthy"
  | "attention"
  | "exceeded";

export interface BudgetOverview {
  year: number;
  month: number;
  configured: boolean;
  monthly_income: string | null;
  reserve_target: string | null;
  spending_limit: string | null;
  spent: string;
  remaining: string | null;
  available_after_reserve: string | null;
  daily_limit: string | null;
  usage_percent: string | null;
  remaining_days: number;
  status: BudgetStatus;
}

export interface BudgetPlanPayload {
  monthly_income: string;
  reserve_target: string;
  spending_limit: string;
}

export interface ReportQuery {
  start_year: number;
  start_month: number;
  end_year: number;
  end_month: number;
  category?: string;
  payment_method?: string;
  place?: string;
}

export interface ReportPeriod {
  start_year: number;
  start_month: number;
  end_year: number;
  end_month: number;
}

export interface ReportMonthlyPoint {
  year: number;
  month: number;
  label: string;
  total: string;
}

export interface ReportCategoryItem {
  name: string;
  total: string;
  percentage: string;
}

export interface ReportMerchantItem {
  name: string;
  total: string;
  transactions: number;
}

export interface ReportInstallmentItem {
  expense_id: number;
  purchase_place: string;
  category: string;
  payment_method: string;
  purchase_value: string;
  owner_total: string;
  total_installments: number;
  paid_installments: number;
  pending_installments: number;
  next_due_date: string | null;
  remaining_amount: string;
}

export interface ReportOverview {
  period: ReportPeriod;
  total_spent: string;
  monthly_average: string;
  transactions: number;
  highest_month: ReportMonthlyPoint | null;
  installment_commitment: string;
  monthly: ReportMonthlyPoint[];
  categories: ReportCategoryItem[];
  merchants: ReportMerchantItem[];
  installments: ReportInstallmentItem[];
}


export type ImportRowStatus = "ready" | "duplicate" | "invalid" | "ignored" | "imported";

export type ImportDateFormat = "auto" | "dmy" | "mdy" | "ymd";
export type ImportDecimalSeparator = "auto" | "comma" | "dot";
export type ImportAmountMode = "all" | "positive" | "negative";

export interface ImportColumnMapping {
  sheet_name: string | null;
  header_row: number | null;
  data_start_row: number;
  date_column: number;
  description_columns: number[];
  amount_column: number | null;
  debit_column: number | null;
  credit_column: number | null;
  external_id_column: number | null;
  date_format: ImportDateFormat;
  decimal_separator: ImportDecimalSeparator;
  amount_mode: ImportAmountMode;
}

export interface ImportInspection {
  source_type: string;
  sheets: string[];
  selected_sheet: string | null;
  total_rows: number;
  max_columns: number;
  rows: string[][];
  mapping_required: boolean;
}

export interface ImportRow {
  id: number;
  row_number: number;
  purchase_date: string | null;
  purchase_place: string | null;
  purchase_value: string | null;
  external_id: string | null;
  status: ImportRowStatus;
  error_message: string | null;
  expense_id: number | null;
}

export interface ImportBatch {
  id: number;
  filename: string;
  source_type: string;
  status: string;
  default_category: string;
  default_payment_method: string;
  total_rows: number;
  ready_rows: number;
  duplicate_rows: number;
  invalid_rows: number;
  imported_rows: number;
  created_at: string;
  completed_at: string | null;
  rows: ImportRow[];
}

export interface ImportHistoryResponse {
  items: ImportBatch[];
}



export interface AutomationSettingsPayload {
  enabled: boolean;
  timezone: string;
  daily_summary_enabled: boolean;
  daily_summary_hour: number;
  weekly_summary_enabled: boolean;
  weekly_summary_weekday: number;
  weekly_summary_hour: number;
  installment_reminders_enabled: boolean;
  installment_reminder_days: number;
  reminder_hour: number;
  budget_alerts_enabled: boolean;
  budget_alert_threshold: number;
}

export interface AutomationSettings
  extends AutomationSettingsPayload {
  telegram_connected: boolean;
}

export interface AutomationMessage {
  kind: string;
  title: string;
  message: string;
  scheduled_for: string | null;
}

export interface AutomationPreviewResponse {
  items: AutomationMessage[];
}

export interface AutomationRunResponse {
  generated: number;
  sent: number;
  skipped: number;
  failed: number;
  items: AutomationMessage[];
}

export interface AutomationDelivery {
  id: number;
  kind: string;
  status: string;
  message: string;
  scheduled_for: string | null;
  sent_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface AutomationHistoryResponse {
  items: AutomationDelivery[];
}


export interface IntelligenceQuery {
  year: number;
  month: number;
}

export interface IntelligenceSummary {
  current_total: string;
  forecast_total: string;
  historical_average: string;
  trend_percent: string | null;
  installment_commitment: string;
  budget_usage_percent: string | null;
  budget_status: string;
  data_months: number;
}

export interface IntelligenceInsight {
  code: string;
  kind: string;
  severity: string;
  title: string;
  message: string;
  recommendation: string;
}

export interface IntelligenceAnomaly {
  expense_id: number;
  purchase_date: string;
  purchase_place: string;
  category: string;
  amount: string;
  category_median: string;
  difference_percent: string;
}

export interface IntelligenceRecurring {
  purchase_place: string;
  category: string;
  occurrences: number;
  average_amount: string;
  last_purchase_date: string;
  expected_next_date: string;
}

export interface IntelligenceOverview {
  year: number;
  month: number;
  generated_at: string;
  summary: IntelligenceSummary;
  monthly: ReportMonthlyPoint[];
  insights: IntelligenceInsight[];
  anomalies: IntelligenceAnomaly[];
  recurring: IntelligenceRecurring[];
}
export interface DashboardComparison {
  previous_month_total: string;
  previous_month_change_percent: string | null;
  year_ago_total: string;
  year_ago_change_percent: string | null;
}

export interface DashboardDailyPoint {
  day: number;
  total: string;
}

export interface DashboardOverview {
  year: number;
  month: number;
  spent: string;
  planned_income: string | null;
  reserve_target: string | null;
  budget_remaining: string | null;
  budget_status: string;
  receivables: string;
  forecast_total: string;
  comparison: DashboardComparison;
  categories: ReportCategoryItem[];
  daily: DashboardDailyPoint[];
  recent_expenses: Expense[];
}

export interface FinanceAgentResponse {
  intent: string;
  answer: string;
  data: Record<string, unknown>;
}
