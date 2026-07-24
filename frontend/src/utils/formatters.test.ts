import { describe, expect, it } from "vitest";

import { formatCurrency, formatDate } from "./formatters";

describe("formatters", () => {
  it("formats Brazilian currency", () => {
    expect(formatCurrency("1234.56")).toContain("1.234,56");
  });

  it("formats ISO date", () => {
    expect(formatDate("2026-07-24T12:00:00")).toBe("24/07/2026");
  });

  it("handles invalid currency", () => {
    expect(formatCurrency("not-a-number")).toContain("0,00");
  });
});
