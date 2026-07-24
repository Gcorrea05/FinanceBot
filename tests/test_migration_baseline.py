from alembic.config import Config
from alembic.script import ScriptDirectory


def test_current_migration_head():
    script = ScriptDirectory.from_config(
        Config("alembic.ini")
    )

    assert script.get_heads() == [
        "20260724_0004"
    ]

    revisions = {
        revision.revision
        for revision in script.walk_revisions()
    }

    assert "20260724_0001" in revisions
    assert "20260724_0004" in revisions
