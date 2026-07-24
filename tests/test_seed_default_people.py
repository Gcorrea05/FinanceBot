from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.constants import DEFAULT_SHARED_PEOPLE
from app.database.base import Base
from app.database.models import Person
from app.database.seed import seed_database


def test_seed_creates_default_people_once():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_database(session)
        seed_database(session)

        names = session.scalars(
            select(Person.name).order_by(
                Person.name
            )
        ).all()

    for expected_name in DEFAULT_SHARED_PEOPLE:
        assert names.count(
            expected_name
        ) == 1
