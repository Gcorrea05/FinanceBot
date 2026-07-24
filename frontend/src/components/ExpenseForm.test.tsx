import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";

import { ExpenseForm } from "./ExpenseForm";


it("submits a simple expense", async () => {
  const user = userEvent.setup();
  const onSubmit = vi.fn().mockResolvedValue(undefined);

  render(
    <ExpenseForm
      categories={["Mercado"]}
      paymentMethods={["Pix"]}
      onCancel={vi.fn()}
      onSubmit={onSubmit}
    />,
  );

  await user.type(screen.getByLabelText("Estabelecimento"), "Mercado Central");
  await user.type(screen.getByLabelText("Valor"), "150,75");
  await user.click(screen.getByRole("button", { name: "Salvar despesa" }));

  expect(onSubmit).toHaveBeenCalledWith(
    expect.objectContaining({
      purchase_place: "Mercado Central",
      purchase_value: "150.75",
      category: "Mercado",
      payment_method: "Pix",
      is_installment: false,
      is_shared: false,
    }),
  );
});
