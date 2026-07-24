from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container


class ImportServiceStub:
    def __init__(self):
        self.preview_args = None

    def preview(self, **kwargs):
        self.preview_args = kwargs
        return self._batch()

    def confirm(self, batch_id):
        batch = self._batch()
        batch.status = "completed"
        batch.imported_rows = 1
        return batch

    def list_history(self, limit=20):
        return [self._batch()]

    def get(self, batch_id):
        return self._batch()

    @staticmethod
    def _batch():
        row = SimpleNamespace(
            id=1,
            row_number=2,
            purchase_date=datetime(2026, 7, 24),
            purchase_place="Mercado",
            purchase_value="10.00",
            external_id=None,
            status="ready",
            error_message=None,
            expense_id=None,
        )
        return SimpleNamespace(
            id=1,
            filename="extrato.csv",
            source_type="csv",
            status="previewed",
            default_category="Outros",
            default_payment_method="Debito",
            total_rows=1,
            ready_rows=1,
            duplicate_rows=0,
            invalid_rows=0,
            imported_rows=0,
            created_at=datetime(2026, 7, 24),
            completed_at=None,
            rows=[row],
        )


def test_preview_import_endpoint():
    application = create_app()
    service = ImportServiceStub()
    application.dependency_overrides[get_container] = lambda: SimpleNamespace(import_service=service)
    client = TestClient(application)
    response = client.post(
        "/api/v1/imports/preview",
        data={"default_category": "Outros", "default_payment_method": "Debito"},
        files={"file": ("extrato.csv", b"data;descricao;valor\n24/07/2026;Mercado;10,00\n", "text/csv")},
    )
    assert response.status_code == 201
    assert response.json()["ready_rows"] == 1
    assert service.preview_args["filename"] == "extrato.csv"
