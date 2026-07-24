import json
from datetime import datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.app import create_app
from app.api.dependencies import get_container


class ImportServiceStub:
    def __init__(self):
        self.preview_args = None
        self.inspect_args = None

    def inspect(self, **kwargs):
        self.inspect_args = kwargs
        return SimpleNamespace(
            source_type="csv",
            sheets=(),
            selected_sheet=None,
            total_rows=2,
            max_columns=3,
            rows=(("QUALQUER", "CABECALHO", "SERVE"), ("24/07/2026", "Mercado", "10,00")),
            mapping_required=True,
        )

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
            filename="fatura.csv",
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


def client_and_service():
    application = create_app()
    service = ImportServiceStub()
    application.dependency_overrides[get_container] = lambda: SimpleNamespace(import_service=service)
    return TestClient(application), service


def test_inspect_import_does_not_require_known_headers():
    client, service = client_and_service()
    response = client.post(
        "/api/v1/imports/inspect",
        files={"file": ("fatura.csv", b"QUALQUER;CABECALHO;SERVE\n24/07/2026;Mercado;10,00\n", "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["rows"][0][0] == "QUALQUER"
    assert service.inspect_args["filename"] == "fatura.csv"


def test_preview_import_endpoint_receives_explicit_mapping():
    client, service = client_and_service()
    mapping = {
        "header_row": 1,
        "data_start_row": 2,
        "date_column": 0,
        "description_columns": [1],
        "amount_column": 2,
        "external_id_column": None,
        "date_format": "dmy",
        "decimal_separator": "comma",
        "amount_mode": "all",
        "sheet_name": None,
    }
    response = client.post(
        "/api/v1/imports/preview",
        data={
            "default_category": "Outros",
            "default_payment_method": "Debito",
            "mapping_json": json.dumps(mapping),
        },
        files={"file": ("fatura.csv", b"QUANDO;ONDE;QUANTO\n24/07/2026;Mercado;10,00\n", "text/csv")},
    )
    assert response.status_code == 201
    assert response.json()["ready_rows"] == 1
    assert service.preview_args["mapping"].date_column == 0
