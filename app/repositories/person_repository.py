from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Person
from app.repositories.base_repository import BaseRepository
from app.utils.text_normalizer import TextNormalizer


class PersonRepository(BaseRepository[Person]):
    def __init__(
        self,
        session: Session,
    ):
        super().__init__(session)

    def get_by_id(
        self,
        person_id: int,
    ) -> Person | None:
        return self.session.get(
            Person,
            person_id,
        )

    def get_by_normalized_name(
        self,
        normalized_name: str,
    ) -> Person | None:
        statement = select(Person).where(
            Person.normalized_name
            == normalized_name
        )

        return self.session.scalar(statement)

    def get_or_create(
        self,
        name: str,
    ) -> Person:
        display_name = " ".join(
            name.strip().split()
        )

        normalized_name = (
            TextNormalizer.normalize(display_name)
        )

        if not normalized_name:
            raise ValueError(
                "O nome da pessoa nao pode ficar vazio."
            )

        existing = self.get_by_normalized_name(
            normalized_name
        )

        if existing is not None:
            return existing

        person = Person(
            name=display_name,
            normalized_name=normalized_name,
        )

        self.session.add(person)

        return person
