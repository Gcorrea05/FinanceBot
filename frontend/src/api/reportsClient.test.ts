import {
  afterEach,
  describe,
  expect,
  it,
  vi,
} from "vitest";

import {
  financeApi,
} from "./client";


afterEach(() => {
  vi.restoreAllMocks();
});


describe("financeApi reports", () => {
  it("loads report filters", async () => {
    const fetchMock = vi
      .spyOn(
        globalThis,
        "fetch",
      )
      .mockResolvedValue(
        new Response(
          JSON.stringify({
            monthly: [],
            categories: [],
            merchants: [],
            installments: [],
          }),
          {
            status: 200,
            headers: {
              "Content-Type": "application/json",
            },
          },
        )
      );

    await financeApi.getReport({
      start_year: 2026,
      start_month: 1,
      end_year: 2026,
      end_month: 7,
      category: "Mercado",
      place: "Central",
    });

    expect(
      fetchMock
    ).toHaveBeenCalledWith(
      expect.stringContaining(
        "/reports/overview?"
      ),
      expect.objectContaining({
        headers: expect.objectContaining({
          Accept: "application/json",
        }),
      }),
    );

    const url = String(
      fetchMock.mock.calls[0][0]
    );

    expect(url).toContain(
      "start_year=2026"
    );
    expect(url).toContain(
      "category=Mercado"
    );
    expect(url).toContain(
      "place=Central"
    );
  });
});
