import { useState } from "react";

import {
  AppShell,
  type PageId,
} from "./components/AppShell";
import { AutomationsPage } from "./pages/AutomationsPage";
import { BudgetPage } from "./pages/BudgetPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ExpensesPage } from "./pages/ExpensesPage";
import { ReceivablesPage } from "./pages/ReceivablesPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ImportsPage } from "./pages/ImportsPage";
import { IntelligencePage } from "./pages/IntelligencePage";

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

      {activePage === "reports"
        ? <ReportsPage />
        : null}

      {activePage === "imports"
        ? <ImportsPage />
        : null}

      {activePage === "automations"
        ? <AutomationsPage />
        : null}

      {activePage === "intelligence"
        ? <IntelligencePage />
        : null}
    </AppShell>
  );
}
