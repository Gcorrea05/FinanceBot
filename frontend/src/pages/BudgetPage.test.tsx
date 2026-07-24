import {
  render,
  screen,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import { financeApi } from "../api/client";
import { BudgetPage } from "./BudgetPage";


vi.mock("../api/client", () => ({
  financeApi: {
    getBudget: vi.fn(),
    saveBudget: vi.fn(),
  },
}));


const mockedApi = vi.mocked(
  financeApi
);


beforeEach(() => {
  mockedApi.getBudget.mockResolvedValue({
    year: 2026,
    month: 7,
    configured: false,
    monthly_income: null,
    reserve_target: null,
    spending_limit: null,
    spent: "150.00",
    remaining: null,
    available_after_reserve: null,
    daily_limit: null,
    usage_percent: null,
    remaining_days: 8,
    status: "not_configured",
  });

  mockedApi.saveBudget.mockResolvedValue({
    year: 2026,
    month: 7,
    configured: true,
    monthly_income: "5000.00",
    reserve_target: "1000.00",
    spending_limit: "3000.00",
    spent: "150.00",
    remaining: "2850.00",
    available_after_reserve: "3850.00",
    daily_limit: "356.25",
    usage_percent: "5.00",
    remaining_days: 8,
    status: "healthy",
  });
});


describe("BudgetPage", () => {
  it("saves a monthly plan", async () => {
    const user = userEvent.setup();

    render(
      <BudgetPage />
    );

    expect(
      await screen.findByRole(
        "heading",
        {
          name: "Planejamento",
        },
      )
    ).toBeInTheDocument();

    await user.type(
      screen.getByLabelText(
        "Renda mensal"
      ),
      "5000.00",
    );

    await user.clear(
      screen.getByLabelText(
        "Meta de reserva"
      )
    );

    await user.type(
      screen.getByLabelText(
        "Meta de reserva"
      ),
      "1000.00",
    );

    await user.type(
      screen.getByLabelText(
        "Limite de gastos"
      ),
      "3000.00",
    );

    await user.click(
      screen.getByRole(
        "button",
        {
          name: "Salvar planejamento",
        },
      )
    );

    expect(
      mockedApi.saveBudget
    ).toHaveBeenCalledWith(
      expect.any(Number),
      expect.any(Number),
      {
        monthly_income: "5000.00",
        reserve_target: "1000.00",
        spending_limit: "3000.00",
      },
    );

    expect(
      await screen.findByText(
        "Planejamento mensal salvo com sucesso."
      )
    ).toBeInTheDocument();
  });
});
