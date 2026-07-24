import { render, screen } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import { financeApi } from "../api/client";
import { ImportsPage } from "./ImportsPage";


vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {},
  financeApi: {
    listCategories: vi.fn(),
    listPaymentMethods: vi.fn(),
    listImports: vi.fn(),
    inspectImport: vi.fn(),
    previewImport: vi.fn(),
    confirmImport: vi.fn(),
  },
}));

const mockedApi = vi.mocked(financeApi);

beforeEach(() => {
  mockedApi.listCategories.mockResolvedValue({ items: [{ name: "Outros" }] });
  mockedApi.listPaymentMethods.mockResolvedValue({ items: [{ name: "Debito" }] });
  mockedApi.listImports.mockResolvedValue({ items: [] });
});

it("renders flexible import controls", async () => {
  render(<ImportsPage />);
  expect(await screen.findByRole("heading", { name: "Importacoes" })).toBeInTheDocument();
  expect(screen.getByText("Ler estrutura")).toBeInTheDocument();
  expect(screen.getByText(/nao exige nomes de colunas/i)).toBeInTheDocument();
  expect(screen.getByText("Historico")).toBeInTheDocument();
});
