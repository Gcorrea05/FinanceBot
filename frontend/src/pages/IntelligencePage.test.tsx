import { render, screen } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { financeApi } from "../api/client";
import { IntelligencePage } from "./IntelligencePage";


vi.mock("../api/client", () => ({
  financeApi: {
    getIntelligenceOverview: vi.fn(),
  },
}));


beforeEach(() => {
  vi.mocked(financeApi.getIntelligenceOverview).mockResolvedValue({
    year: 2026,
    month: 7,
    generated_at: "2026-07-24T20:00:00",
    summary: {
      current_total: "900.00",
      forecast_total: "1200.00",
      historical_average: "800.00",
      trend_percent: "12.50",
      installment_commitment: "400.00",
      budget_usage_percent: "45.00",
      budget_status: "healthy",
      data_months: 5,
    },
    monthly: [{ year: 2026, month: 7, label: "Jul/26", total: "900.00" }],
    insights: [{
      code: "stable",
      kind: "summary",
      severity: "positive",
      title: "Periodo estavel",
      message: "Sem desvios importantes.",
      recommendation: "Continue acompanhando.",
    }],
    anomalies: [],
    recurring: [],
  });
});


test("loads financial intelligence", async () => {
  render(<IntelligencePage />);
  expect(await screen.findByRole("heading", { name: "Inteligencia financeira" })).toBeInTheDocument();
  expect(screen.getByText("Periodo estavel")).toBeInTheDocument();
});
