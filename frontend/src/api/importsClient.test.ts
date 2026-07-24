import { afterEach, expect, it, vi } from "vitest";

import { financeApi } from "./client";

afterEach(() => vi.restoreAllMocks());

it("sends multipart import preview", async () => {
  const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify({ id: 1, rows: [] }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    }),
  );
  const file = new File(["data;descricao;valor"], "extrato.csv", { type: "text/csv" });
  await financeApi.previewImport(file, "Outros", "Debito");
  const request = fetchMock.mock.calls[0][1];
  expect(request?.method).toBe("POST");
  expect(request?.body).toBeInstanceOf(FormData);
  expect(request?.headers).not.toHaveProperty("Content-Type");
});
