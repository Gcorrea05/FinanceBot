import {
  render,
  screen,
} from "@testing-library/react";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  financeApi,
} from "../api/client";
import {
  ReportsPage,
} from "./ReportsPage";


vi.mock("../api/client", () => ({
  financeApi: {
    getReport: vi.fn(),
    listCategories: vi.fn(),
    listPaymentMethods: vi.fn(),
  },
}));


const mockedApi = vi.mocked(
  financeApi
);


beforeEach(() => {
  mockedApi.listCategories.mockResolvedValue({
    items: [
      {
        name: "Mercado",
      },
    ],
  });

  mockedApi.listPaymentMethods.mockResolvedValue({
    items: [
      {
        name: "Pix",
      },
    ],
  });

  mockedApi.getReport.mockResolvedValue({
    period: {
      start_year: 2026,
      start_month: 2,
      end_year: 2026,
      end_month: 7,
    },
    total_spent: "1200.00",
    monthly_average: "200.00",
    transactions: 8,
    highest_month: {
      year: 2026,
      month: 7,
      label: "Jul/26",
      total: "400.00",
    },
    installment_commitment: "300.00",
    monthly: [
      {
        year: 2026,
        month: 7,
        label: "Jul/26",
        total: "400.00",
      },
    ],
    categories: [
      {
        name: "Mercado",
        total: "400.00",
        percentage: "33.33",
      },
    ],
    merchants: [
      {
        name: "Mercado Central",
        total: "400.00",
        transactions: 2,
      },
    ],
    installments: [],
  });
});


describe("ReportsPage", () => {
  it("renders analytical summaries", async () => {
    render(
      <ReportsPage />
    );

    expect(
      await screen.findByRole(
        "heading",
        {
          name: "Relatorios",
        },
      )
    ).toBeInTheDocument();

    expect(
      await screen.findByText(
        "R$ 1.200,00"
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText(
        "Mercado Central"
      )
    ).toBeInTheDocument();

    expect(
      mockedApi.getReport
    ).toHaveBeenCalledOnce();
  });
});
