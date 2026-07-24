from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models.import_batch import ImportBatch, ImportRow


class ImportRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_batch(self, batch: ImportBatch) -> ImportBatch:
        self.session.add(batch)
        self.session.flush()
        return batch

    def add_rows(self, rows: Iterable[ImportRow]) -> None:
        self.session.add_all(list(rows))
        self.session.flush()

    def get_batch(self, batch_id: int) -> ImportBatch | None:
        statement = (
            select(ImportBatch)
            .options(selectinload(ImportBatch.rows))
            .where(ImportBatch.id == batch_id)
        )
        return self.session.scalar(statement)

    def list_batches(self, limit: int = 20) -> list[ImportBatch]:
        statement = (
            select(ImportBatch)
            .order_by(ImportBatch.created_at.desc(), ImportBatch.id.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def existing_fingerprints(self, fingerprints: set[str]) -> set[str]:
        if not fingerprints:
            return set()
        statement = select(ImportRow.fingerprint).where(
            ImportRow.fingerprint.in_(fingerprints),
            ImportRow.status == "imported",
        )
        return {value for value in self.session.scalars(statement).all() if value}

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
