import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { financeApi } from "./api/client";
import { App } from "./App";

vi.mock("./api/client", async () => {
  const actual = await vi.importActual<typeof import("./api/client")>("./api/client");

  return {
    ...actual,
    financeApi: {
      ready: vi.fn(),
      listExpenses: vi.fn(),
      listReceivables: vi.fn(),
      listPersonReceivables: vi.fn(),
      settleReceivable: vi.fn(),
    },
  };
});

const mockedApi = vi.mocked(financeApi);

beforeEach(() => {
  mockedApi.ready.mockResolvedValue({ status: "ready" });
  mockedApi.listExpenses.mockResolvedValue({
    items: [],
    total: 0,
    limit: 100,
    offset: 0,
  });
  mockedApi.listReceivables.mockResolvedValue({
    people: [],
    total_general: "0.00",
  });
});

describe("App", () => {
  it("renders the dashboard and navigates to expenses", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Visao geral" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /Despesas/i }));

    expect(await screen.findByRole("heading", { name: "Despesas" })).toBeInTheDocument();
  });
});
