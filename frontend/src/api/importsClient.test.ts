import { afterEach, expect, it, vi } from "vitest";

import { financeApi } from "./client";


afterEach(() => vi.restoreAllMocks());

it("sends multipart inspection without requiring known columns", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ source_type: "csv", rows: [] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
  const file = new File(["QUALQUER;CABECALHO"], "fatura.csv", { type: "text/csv" });
  await financeApi.inspectImport(file);
  const request = fetchMock.mock.calls[0][1];
  expect(fetchMock.mock.calls[0][0]).toContain("/imports/inspect");
  expect(request?.method).toBe("POST");
  expect(request?.body).toBeInstanceOf(FormData);
});

it("sends explicit mapping with the preview request", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ id: 1, rows: [] }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    }),
  );
  const file = new File(["QUANDO;ONDE;QUANTO"], "fatura.csv", { type: "text/csv" });
  await financeApi.previewImport(file, "Outros", "Debito", {
    sheet_name: null,
    header_row: 1,
    data_start_row: 2,
    date_column: 0,
    description_columns: [1],
    amount_column: 2,
    external_id_column: null,
    date_format: "dmy",
    decimal_separator: "comma",
    amount_mode: "all",
  });
  const request = fetchMock.mock.calls[0][1];
  const body = request?.body as FormData;
  expect(body.get("mapping_json")).toContain('"date_column":0');
  expect(request?.headers).not.toHaveProperty("Content-Type");
});
