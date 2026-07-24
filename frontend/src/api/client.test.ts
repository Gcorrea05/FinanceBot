import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, financeApi } from "./client";
import type { ExpenseMutationPayload } from "./types";


afterEach(() => {
  vi.restoreAllMocks();
});

const payload: ExpenseMutationPayload = {
  purchase_date: "2026-07-24T10:00:00",
  purchase_place: "Mercado Central",
  purchase_value: "150.75",
  category: "Mercado",
  payment_method: "Pix",
  is_installment: false,
  installments: 1,
  first_installment_due_date: null,
  is_shared: false,
  shared_people: [],
  notes: null,
};


describe("financeApi", () => {
  it("loads expenses with query parameters", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({ items: [], total: 0, limit: 10, offset: 0 }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );

    await financeApi.listExpenses({ limit: 10, month: 7, year: 2026 });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/expenses?limit=10&month=7&year=2026"),
      expect.objectContaining({
        headers: expect.objectContaining({ Accept: "application/json" }),
      }),
    );
  });

  it("sends create and update payloads", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockImplementation(() =>
        Promise.resolve(
          new Response(JSON.stringify({ id: 10 }), {
            status: 200,
            headers: {
              "Content-Type": "application/json",
            },
          }),
        ),
      );

    await financeApi.createExpense(payload);
    await financeApi.updateExpense(10, payload);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      expect.stringContaining("/expenses"),
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      expect.stringContaining("/expenses/10"),
      expect.objectContaining({ method: "PUT" }),
    );
  });

  it("deletes an expense", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(null, { status: 204 }),
    );

    await financeApi.deleteExpense(10);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/expenses/10"),
      expect.objectContaining({ method: "DELETE" }),
    );
  });

  it("raises ApiError for unavailable API", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));

    await expect(financeApi.ready()).rejects.toBeInstanceOf(ApiError);
  });
});
