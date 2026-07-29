from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import unicodedata


@dataclass(frozen=True)
class FinanceAgentAnswer:
    intent: str
    answer: str
    data: dict


class FinanceAgent:
    def __init__(self, *, dashboard_service, receivable_service):
        self.dashboard_service = dashboard_service
        self.receivable_service = receivable_service

    def answer(
        self,
        question: str,
        *,
        today: date | None = None,
    ) -> FinanceAgentAnswer:
        current = today or date.today()
        normalized = self._normalize(question)
        dashboard = self.dashboard_service.get_overview(
            year=current.year,
            month=current.month,
        )

        if "quem me deve" in normalized or "valores a receber" in normalized:
            rows = self.receivable_service.list_open_summary()
            total = sum(
                (item.total for item in rows),
                start=Decimal("0.00"),
            )
            return FinanceAgentAnswer(
                intent="receivables",
                answer=f"Ha R$ {total:.2f} em valores a receber.",
                data={
                    "total": str(total),
                    "people": [
                        {
                            "name": item.person_name,
                            "total": str(item.total),
                        }
                        for item in rows
                    ],
                },
            )

        if "categoria" in normalized and (
            "maior" in normalized or "mais" in normalized
        ):
            top = dashboard.categories[0] if dashboard.categories else None
            if top is None:
                return FinanceAgentAnswer(
                    intent="top_category",
                    answer="Nao ha despesas suficientes neste mes.",
                    data={},
                )
            return FinanceAgentAnswer(
                intent="top_category",
                answer=f"A categoria {top.name} lidera o mes com R$ {top.total:.2f}.",
                data={
                    "category": top.name,
                    "total": str(top.total),
                    "percentage": str(top.percentage),
                },
            )

        if "orcamento" in normalized or "limite" in normalized:
            remaining = dashboard.budget_remaining
            if remaining is None:
                return FinanceAgentAnswer(
                    intent="budget",
                    answer="O planejamento deste mes ainda nao foi configurado.",
                    data={"status": dashboard.budget_status},
                )
            return FinanceAgentAnswer(
                intent="budget",
                answer=f"O limite restante e R$ {remaining:.2f}.",
                data={
                    "remaining": str(remaining),
                    "status": dashboard.budget_status,
                },
            )

        if "previsao" in normalized or "projecao" in normalized:
            return FinanceAgentAnswer(
                intent="forecast",
                answer=f"A projecao do mes e R$ {dashboard.forecast_total:.2f}.",
                data={"forecast_total": str(dashboard.forecast_total)},
            )

        if (
            "gastei" in normalized
            or "gasto" in normalized
            or "despesa" in normalized
        ):
            return FinanceAgentAnswer(
                intent="monthly_spending",
                answer=f"O gasto considerado neste mes e R$ {dashboard.spent:.2f}.",
                data={
                    "spent": str(dashboard.spent),
                    "year": dashboard.year,
                    "month": dashboard.month,
                },
            )

        return FinanceAgentAnswer(
            intent="help",
            answer=(
                "Posso informar gastos do mes, previsao, orcamento, "
                "categoria principal e valores a receber."
            ),
            data={
                "capabilities": [
                    "monthly_spending",
                    "forecast",
                    "budget",
                    "top_category",
                    "receivables",
                ]
            },
        )

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value)
        return "".join(
            character
            for character in decomposed
            if not unicodedata.combining(character)
        ).lower().strip()
