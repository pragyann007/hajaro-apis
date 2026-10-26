import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# 1. Add project root to Python path so 'app' can be found
# Add this filter function inside alembic/env.py
def include_object(object, name, type_, reflected, compare_to):
    # Ignore automatic geoalchemy spatial index generation duplicates
    if type_ == "index" and name and name.startswith("idx_"):
        if any(col.name == "geographic_point" for col in object.table.columns):
            return False
    return True
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Setup Alembic configuration and logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Import Base from your models package bundle
from app.hajaro.models import Base
target_metadata = Base.metadata

# Get the database URL from alembic.ini
db_url = config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Helper connection block executing inside the sync runner wrapper."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an AsyncEngine."""
    # Build an async engine directly using your async connection string
    connectable = create_async_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Crucial fix: wrapper that maps async execution to alembic's sync requirements
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Safely execute the async orchestration loop
    asyncio.run(run_migrations_online())
