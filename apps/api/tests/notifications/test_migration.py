"""Test Stage 49 migration revision definitions and structure."""

import importlib.util
from pathlib import Path


def test_stage49_migration_revision():
    migration_path = (
        Path(__file__).parents[2]
        / "migrations"
        / "versions"
        / "7e8f9012abcd_stage49_notifications.py"
    )
    assert migration_path.exists(), f"Migration file not found at {migration_path}"

    spec = importlib.util.spec_from_file_location("stage49_migration", migration_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "7e8f9012abcd"
    assert module.down_revision == "6cf729b2c092"
    assert callable(module.upgrade)
    assert callable(module.downgrade)
