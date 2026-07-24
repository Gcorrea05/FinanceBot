import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, financeApi } from "./client";

afterEach(() => {
  vi.restoreAllMocks();
});

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

  it("raises ApiError for unavailable API", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("offline"));

    await expect(financeApi.ready()).rejects.toBeInstanceOf(ApiError);
  });
});
