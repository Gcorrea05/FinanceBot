import {
  render,
  screen,
} from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { financeApi } from "../api/client";
import { AutomationsPage } from "./AutomationsPage";


vi.mock("../api/client", () => ({
  financeApi: {
    getAutomationSettings: vi.fn(),
    previewAutomations: vi.fn(),
    listAutomationDeliveries: vi.fn(),
    saveAutomationSettings: vi.fn(),
    runAutomationsNow: vi.fn(),
    disconnectTelegram: vi.fn(),
  },
}));


beforeEach(() => {
  vi.mocked(
    financeApi.getAutomationSettings
  ).mockResolvedValue({
    enabled: true,
    telegram_connected: true,
    timezone: "America/Sao_Paulo",
    daily_summary_enabled: true,
    daily_summary_hour: 20,
    weekly_summary_enabled: true,
    weekly_summary_weekday: 0,
    weekly_summary_hour: 8,
    installment_reminders_enabled: true,
    installment_reminder_days: 3,
    reminder_hour: 9,
    budget_alerts_enabled: true,
    budget_alert_threshold: 80,
  });

  vi.mocked(
    financeApi.previewAutomations
  ).mockResolvedValue({
    items: [],
  });

  vi.mocked(
    financeApi.listAutomationDeliveries
  ).mockResolvedValue({
    items: [],
  });
});


test(
  "loads automation settings",
  async () => {
    render(
      <AutomationsPage />
    );

    expect(
      await screen.findByRole(
        "heading",
        {
          name: "Automacoes",
        },
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Enviar teste agora"
      )
    ).toBeInTheDocument();
  },
);
