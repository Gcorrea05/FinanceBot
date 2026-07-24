from types import SimpleNamespace

from app.imports.parser import ImportColumnMapping
from app.services.import_service import ImportService


class LookupStub:
    def get_category(self, name):
        return SimpleNamespace(name=name)

    def get_payment_method(self, name):
        return SimpleNamespace(name=name)


class RepositoryStub:
    def __init__(self):
        self.batch = None
        self.rows = []

    def existing_fingerprints(self, fingerprints):
        return set()

    def add_batch(self, batch):
        batch.id = 1
        batch.rows = []
        self.batch = batch
        return batch

    def add_rows(self, rows):
        self.rows = list(rows)
        for index, row in enumerate(self.rows, start=1):
            row.id = index
        self.batch.rows = self.rows

    def commit(self):
        return None

    def get_batch(self, batch_id):
        return self.batch if batch_id == 1 else None

    def list_batches(self, limit=20):
        return [self.batch] if self.batch else []


class ExpenseServiceStub:
    def create_expense(self, data):
        return SimpleNamespace(id=99)


def mapping():
    return ImportColumnMapping(
        data_start_row=2,
        date_column=0,
        description_columns=(1,),
        amount_column=2,
        date_format="dmy",
        decimal_separator="comma",
    )


def test_preview_marks_duplicate_inside_same_file_with_custom_headers():
    repository = RepositoryStub()
    service = ImportService(repository, ExpenseServiceStub(), LookupStub())
    content = (
        "QUANDO;ONDE;QUANTO\n"
        "24/07/2026;Mercado;10,00\n"
        "24/07/2026;Mercado;10,00\n"
    ).encode("utf-8")
    batch = service.preview(
        filename="fatura.csv",
        content=content,
        default_category="Outros",
        default_payment_method="Debito",
        mapping=mapping(),
    )
    assert batch.ready_rows == 1
    assert batch.duplicate_rows == 1
