import { afterEach, describe, expect, it, vi } from "vitest";

import { financeApi } from "./client";


describe("alignment API", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("downloads the selected monthly Excel", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(new Blob(["xlsx"]), { status: 200 }),
    );

    const result = await financeApi.downloadMonthlyExcel(2026, 7);

    expect(result).toBeInstanceOf(Blob);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exports/monthly.xlsx?year=2026&month=7"),
      expect.any(Object),
    );
  });

  it("reopens a settled receivable", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          receivable_id: 4,
          is_settled: false,
          settled_at: null,
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      ),
    );

    const result = await financeApi.reopenReceivable(4);

    expect(result.is_settled).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/receivables/4/reopen"),
      expect.objectContaining({ method: "POST" }),
    );
  });
});
