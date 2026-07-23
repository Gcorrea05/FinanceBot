from unittest.mock import patch

from app.container import container_context


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True

    def rollback(self):
        pass


def test_container_context_closes_session():
    session = FakeSession()
    container = object()

    with (
        patch(
            "app.container.get_session",
            return_value=session,
        ),
        patch(
            "app.container.Container",
            return_value=container,
        ),
    ):
        with container_context() as resolved:
            assert resolved is container
            assert session.closed is False

    assert session.closed is True
