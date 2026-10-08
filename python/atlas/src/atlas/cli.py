import argparse
import sys
import asyncio
from atlas.infrastructure.clickhouse.settings import ClickHouseSettings
from atlas.infrastructure.clickhouse.client import ClickHouseClientFactory
from atlas.infrastructure.clickhouse.migrations.runner import run_migrations

def ch_migrate():
    settings = ClickHouseSettings()
    factory = ClickHouseClientFactory(settings)
    try:
        run_migrations(factory)
        print("ClickHouse migrations completed successfully.")
    except Exception as e:
        print(f"Error running ClickHouse migrations: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        factory.close()

def main():
    parser = argparse.ArgumentParser(description="Atlas CLI Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    ch_parser = subparsers.add_parser("ch-migrate", help="Run ClickHouse migrations")
    
    args = parser.parse_args()
    
    if args.command == "ch-migrate":
        ch_migrate()

if __name__ == "__main__":
    main()
