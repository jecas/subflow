from pathlib import Path


def test_initial_migration_exists() -> None:
    migration = Path(
        "alembic/versions/0001_initial_schema.py"
    )

    assert migration.exists()


def test_alembic_configuration_exists() -> None:
    assert Path("alembic.ini").exists()
    assert Path("alembic/env.py").exists()
