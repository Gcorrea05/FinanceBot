from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.agents import FinanceAgent


class DashboardStub:
    def get_overview(self, *, year, month):
        return SimpleNamespace(
            year=year,
            month=month,
            spent=Decimal("450.00"),
            forecast_total=Decimal("700.00"),
            budget_remaining=Decimal("550.00"),
            budget_status="healthy",
            categories=[
                SimpleNamespace(
                    name="Mercado",
                    total=Decimal("200.00"),
                    percentage=Decimal("44.44"),
                )
            ],
        )


class ReceivableStub:
    def list_open_summary(self):
        return [
            SimpleNamespace(
                person_name="Tomas",
                total=Decimal("80.00"),
            )
        ]


def test_agent_uses_services_instead_of_database():
    agent = FinanceAgent(
        dashboard_service=DashboardStub(),
        receivable_service=ReceivableStub(),
    )
    result = agent.answer(
        "Quanto gastei este mes?",
        today=date(2026, 7, 20),
    )

    assert result.intent == "monthly_spending"
    assert result.data["spent"] == "450.00"
