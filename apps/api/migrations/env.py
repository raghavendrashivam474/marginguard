"""MarginGuard Alembic environment configuration.

This file is executed by Alembic during migration operations. It configures
the SQLAlchemy engine and provides the target metadata for autogenerate.

Key decisions (see ADR-005):
- DATABASE_URL is read from app.core.config.settings (same as the app)
- Supports both online (live DB) and offline (SQL script) modes
- Imports Base.metadata from infrastructure models for autogenerate
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Alembic Config object
config = context.config

# Set up Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the SQLAlchemy Base metadata for autogenerate support.
# This must happen AFTER fileConfig to avoid import-order issues.
from app.infrastructure.models import Base  # noqa: E402

target_metadata = Base.metadata


def get_url() -> str:
    """Resolve the database URL from application settings."""
    from app.core.config import settings

    url = settings.DATABASE_URL
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Set it in .env or as an environment variable."
        )
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to a database.
    Useful for review before applying to production.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Connects to the database and applies migrations directly.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
