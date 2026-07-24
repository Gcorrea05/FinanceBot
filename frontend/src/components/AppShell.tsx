import type { ReactNode } from "react";

export type PageId = "dashboard" | "expenses" | "receivables";

interface AppShellProps {
  activePage: PageId;
  onNavigate: (page: PageId) => void;
  children: ReactNode;
}

const navigation: Array<{ id: PageId; label: string; description: string }> = [
  {
    id: "dashboard",
    label: "Visao geral",
    description: "Resumo financeiro",
  },
  {
    id: "expenses",
    label: "Despesas",
    description: "Historico e filtros",
  },
  {
    id: "receivables",
    label: "Valores a receber",
    description: "Pendencias compartilhadas",
  },
];

export function AppShell({ activePage, onNavigate, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">FB</span>
          <div>
            <strong>FinanceBot</strong>
            <span>Painel pessoal</span>
          </div>
        </div>

        <nav className="navigation" aria-label="Navegacao principal">
          {navigation.map((item) => (
            <button
              className={item.id === activePage ? "nav-item active" : "nav-item"}
              key={item.id}
              onClick={() => onNavigate(item.id)}
              type="button"
            >
              <strong>{item.label}</strong>
              <span>{item.description}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-note">
          <strong>Telegram operacional</strong>
          <span>Continue usando o bot para registrar despesas rapidamente.</span>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
