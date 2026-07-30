import { afterEach, describe, expect, it, vi } from "vitest";

import { financeApi } from "./client";


describe("alignment API", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("downloads the selected monthly Excel", async () => {
    const excelBlob = {
      size: 4,
      type:
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    } as Blob;

    const blobMock = vi.fn().mockResolvedValue(excelBlob);

    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      {
        ok: true,
        status: 200,
        blob: blobMock,
      } as unknown as Response,
    );

    const result = await financeApi.downloadMonthlyExcel(2026, 7);

    expect(result).toBe(excelBlob);
    expect(blobMock).toHaveBeenCalledOnce();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exports/monthly.xlsx?year=2026&month=7"),
      expect.objectContaining({
        headers: expect.objectContaining({
          Accept:
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }),
      }),
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