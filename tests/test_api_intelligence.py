from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container
from app.services.intelligence_service import (
    IntelligenceInsight,
    IntelligenceOverview,
    IntelligenceSummary,
)
from app.services.report_service import MonthlyReportPoint


class ServiceStub:
    def get_overview(self, **kwargs):
        self.received = kwargs
        return IntelligenceOverview(
            year=2026,
            month=7,
            generated_at=datetime(2026, 7, 24, 20, 0),
            summary=IntelligenceSummary(
                current_total=Decimal('900.00'),
                forecast_total=Decimal('1200.00'),
                historical_average=Decimal('800.00'),
                trend_percent=Decimal('12.50'),
                installment_commitment=Decimal('300.00'),
                budget_usage_percent=Decimal('45.00'),
                budget_status='healthy',
                data_months=5,
            ),
            monthly=[MonthlyReportPoint(year=2026, month=7, label='Jul/26', total=Decimal('900.00'))],
            insights=[IntelligenceInsight(code='stable', kind='summary', severity='positive', title='Estavel', message='Ok', recommendation='Continue')],
            anomalies=[],
            recurring=[],
        )


def test_get_intelligence_overview():
    app = create_app()
    service = ServiceStub()
    app.dependency_overrides[get_container] = lambda: SimpleNamespace(intelligence_service=service)
    response = TestClient(app).get('/api/v1/intelligence/overview?year=2026&month=7')
    assert response.status_code == 200
    assert response.json()['summary']['forecast_total'] == '1200.00'
    assert service.received['year'] == 2026
