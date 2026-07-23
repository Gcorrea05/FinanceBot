from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(String(255))

    status: Mapped[str] = mapped_column(String(30))

    imported_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )