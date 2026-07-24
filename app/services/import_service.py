from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.database.models.import_batch import ImportBatch, ImportRow
from app.imports.parser import (
    ImportColumnMapping,
    ImportFileError,
    ImportInspection,
    inspect_import_file,
    parse_import_file,
)
from app.repositories.import_repository import ImportRepository
from app.schemas.expense.create import ExpenseCreate

if TYPE_CHECKING:
    from app.services.expense_service import ExpenseService
    from app.services.lookup_service import LookupService


class ImportBatchNotFoundError(LookupError):
    pass


class ImportConflictError(RuntimeError):
    pass


class ImportService:
    def __init__(
        self,
        repository: ImportRepository,
        expense_service: ExpenseService,
        lookup_service: LookupService,
    ):
        self.repository = repository
        self.expense_service = expense_service
        self.lookup_service = lookup_service

    def inspect(
        self,
        *,
        filename: str,
        content: bytes,
        sheet_name: str | None = None,
    ) -> ImportInspection:
        return inspect_import_file(
            filename,
            content,
            sheet_name=sheet_name,
        )

    def preview(
        self,
        *,
        filename: str,
        content: bytes,
        default_category: str,
        default_payment_method: str,
        mapping: ImportColumnMapping | None = None,
    ) -> ImportBatch:
        self.lookup_service.get_category(default_category)
        self.lookup_service.get_payment_method(default_payment_method)
        parsed = parse_import_file(filename, content, mapping)

        fingerprints = {row.fingerprint for row in parsed.rows if row.fingerprint}
        existing = self.repository.existing_fingerprints(fingerprints)
        seen: set[str] = set()
        ready = duplicate = invalid = ignored = 0

        batch = self.repository.add_batch(
            ImportBatch(
                filename=filename[:255],
                source_type=parsed.source_type,
                status="previewed",
                default_category=default_category,
                default_payment_method=default_payment_method,
                total_rows=len(parsed.rows),
            )
        )

        records: list[ImportRow] = []
        for row in parsed.rows:
            if row.ignored:
                status = "ignored"
                ignored += 1
            elif not row.valid:
                status = "invalid"
                invalid += 1
            elif row.fingerprint in existing or row.fingerprint in seen:
                status = "duplicate"
                duplicate += 1
            else:
                status = "ready"
                ready += 1
                if row.fingerprint:
                    seen.add(row.fingerprint)

            records.append(
                ImportRow(
                    batch_id=batch.id,
                    row_number=row.row_number,
                    purchase_date=row.purchase_date,
                    purchase_place=row.purchase_place,
                    purchase_value=row.purchase_value,
                    external_id=row.external_id,
                    fingerprint=row.fingerprint,
                    status=status,
                    error_message=(
                        row.error_message
                        if status in {"invalid", "ignored"}
                        else "Transacao duplicada."
                        if status == "duplicate"
                        else None
                    ),
                )
            )

        batch.ready_rows = ready
        batch.duplicate_rows = duplicate
        batch.invalid_rows = invalid
        self.repository.add_rows(records)
        self.repository.commit()
        detailed = self.repository.get_batch(batch.id)
        if detailed is None:
            raise RuntimeError("Falha ao recuperar a pre-visualizacao criada.")
        return detailed

    def confirm(self, batch_id: int) -> ImportBatch:
        batch = self.repository.get_batch(batch_id)
        if batch is None:
            raise ImportBatchNotFoundError(f"Importacao {batch_id} nao encontrada.")
        if batch.status != "previewed":
            raise ImportConflictError("Esta importacao ja foi confirmada ou encerrada.")

        imported = 0
        for row in batch.rows:
            if row.status != "ready":
                continue
            if row.purchase_date is None or row.purchase_place is None or row.purchase_value is None:
                row.status = "invalid"
                row.error_message = "Linha incompleta durante a confirmacao."
                continue

            try:
                expense = self.expense_service.create_expense(
                    ExpenseCreate(
                        purchase_date=row.purchase_date,
                        purchase_place=row.purchase_place,
                        purchase_value=row.purchase_value,
                        category=batch.default_category,
                        payment_method=batch.default_payment_method,
                        notes=f"Importado de {batch.filename}",
                    )
                )
            except Exception as error:
                row.status = "invalid"
                row.error_message = str(error)
                continue

            row.status = "imported"
            row.expense_id = expense.id
            imported += 1

        batch.imported_rows = imported
        batch.ready_rows = 0
        batch.invalid_rows = sum(1 for row in batch.rows if row.status == "invalid")
        batch.status = "completed"
        batch.completed_at = datetime.utcnow()
        self.repository.commit()
        detailed = self.repository.get_batch(batch.id)
        if detailed is None:
            raise RuntimeError("Falha ao recuperar a importacao confirmada.")
        return detailed

    def get(self, batch_id: int) -> ImportBatch:
        batch = self.repository.get_batch(batch_id)
        if batch is None:
            raise ImportBatchNotFoundError(f"Importacao {batch_id} nao encontrada.")
        return batch

    def list_history(self, limit: int = 20) -> list[ImportBatch]:
        return self.repository.list_batches(limit=limit)


__all__ = [
    "ImportBatchNotFoundError",
    "ImportConflictError",
    "ImportFileError",
    "ImportService",
]
