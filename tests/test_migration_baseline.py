from alembic.config import Config
from alembic.script import ScriptDirectory


def test_single_baseline_head():
    script = ScriptDirectory.from_config(
        Config("alembic.ini")
    )

    assert script.get_heads() == [
        "20260724_0001"
    ]
