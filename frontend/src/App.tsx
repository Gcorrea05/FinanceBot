import { useState } from "react";

import {
  AppShell,
  type PageId,
} from "./components/AppShell";
import { BudgetPage } from "./pages/BudgetPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ExpensesPage } from "./pages/ExpensesPage";
import { ReceivablesPage } from "./pages/ReceivablesPage";

export function App() {
  const [
    activePage,
    setActivePage,
  ] = useState<PageId>(
    "dashboard"
  );

  return (
    <AppShell
      activePage={activePage}
      onNavigate={setActivePage}
    >
      {activePage === "dashboard"
        ? <DashboardPage />
        : null}

      {activePage === "expenses"
        ? <ExpensesPage />
        : null}

      {activePage === "receivables"
        ? <ReceivablesPage />
        : null}

      {activePage === "budget"
        ? <BudgetPage />
        : null}
    </AppShell>
  );
}
