from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.container import Container
from app.database.session import get_session


def get_session_dependency() -> Iterator[Session]:
    session = get_session()

    try:
        yield session

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_container(
    session: Session = Depends(
        get_session_dependency
    ),
) -> Container:
    return Container(session)
