import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import os

import atlas.authorization.models  # noqa: F401
import atlas.companies.models  # noqa: F401
import atlas.entities.models  # noqa: F401
import atlas.geography.models  # noqa: F401
import atlas.instruments.models  # noqa: F401
import atlas.economics.models  # noqa: F401
import atlas.research.models  # noqa: F401
import atlas.news.models  # noqa: F401
import atlas.preferences.models  # noqa: F401
import atlas.identifiers.models  # noqa: F401
import atlas.aliases.models  # noqa: F401
import atlas.relationships.models  # noqa: F401
import atlas.provenance.models  # noqa: F401
import atlas.providers.configuration.models  # noqa: F401
import atlas.providers.health.db_models  # noqa: F401
import atlas.providers.routing.db_models  # noqa: F401
import atlas.market_data.models  # noqa: F401
import atlas.market_data.updates.models  # noqa: F401
import atlas.market_data.live.models  # noqa: F401
import atlas.activity.models  # noqa: F401
import atlas.tasks.models  # noqa: F401
import atlas.approvals.models  # noqa: F401
from atlas.database import Base, normalize_database_url

from atlas_api.config import get_settings

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Set SQLAlchemy URL from settings
settings = get_settings()
# Use test database if running in test environment
db_url = (
    settings.test_database_url if os.environ.get("ATLAS_ENV") == "test" else settings.database_url
)
config.set_main_option("sqlalchemy.url", normalize_database_url(db_url))

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
