import hashlib
import logging
from pathlib import Path
from atlas.infrastructure.clickhouse.client import ClickHouseClientFactory
from clickhouse_connect.driver.client import Client as ClickHouseClient

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "sql"

def _ensure_migrations_table(client: ClickHouseClient):
    client.command("""
        CREATE TABLE IF NOT EXISTS atlas_schema_migrations (
            version String,
            checksum String,
            applied_at DateTime64(6, 'UTC') DEFAULT now64()
        ) ENGINE = MergeTree()
        ORDER BY version
    """)

def _get_applied_migrations(client: ClickHouseClient) -> dict[str, str]:
    result = client.query("SELECT version, checksum FROM atlas_schema_migrations ORDER BY version")
    return {row[0]: row[1] for row in result.result_rows}

def run_migrations(factory: ClickHouseClientFactory):
    """
    Apply all pending ClickHouse migrations in the sql/ directory.
    This is deterministic and idempotent.
    """
    client = factory.get_client()
    if not client:
        logger.warning("ClickHouse is disabled. Skipping migrations.")
        return

    _ensure_migrations_table(client)
    applied = _get_applied_migrations(client)
    
    if not MIGRATIONS_DIR.exists():
        logger.info(f"No migrations directory found at {MIGRATIONS_DIR}")
        return

    sql_files = sorted([f for f in MIGRATIONS_DIR.iterdir() if f.suffix == '.sql'])
    
    for sql_file in sql_files:
        version = sql_file.stem
        content = sql_file.read_text(encoding='utf-8')
        checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        if version in applied:
            if applied[version] != checksum:
                raise ValueError(f"Migration checksum mismatch for {version}. Has it been modified?")
            logger.debug(f"Migration {version} already applied.")
            continue
            
        logger.info(f"Applying ClickHouse migration: {version}")
        
        # Split statements if necessary. For now we assume one statement or use multiline appropriately.
        # clickhouse-connect command runs a single statement. If file contains multiple statements,
        # we might need to parse. But usually standard schema changes are done in single statements.
        statements = [s.strip() for s in content.split(';') if s.strip()]
        for stmt in statements:
            client.command(stmt)
            
        client.command(
            "INSERT INTO atlas_schema_migrations (version, checksum) VALUES",
            [[version, checksum]]
        )
        logger.info(f"Successfully applied {version}.")
