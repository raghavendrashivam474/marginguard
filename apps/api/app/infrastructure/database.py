"""MarginGuard infrastructure — database engine and session management.

Provides lazy engine creation so the application can boot (e.g. for /health)
even when no database is available. The engine is created on first access.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

_engine = None
_SessionLocal = None


def get_engine():
    """Lazily create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        url = settings.DATABASE_URL
        if not url:
            raise RuntimeError(
                "DATABASE_URL is not configured. "
                "Set it in .env or as an environment variable."
            )
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        _engine = create_engine(
            url,
            echo=settings.LOG_LEVEL == "DEBUG",
            connect_args=connect_args,
            pool_pre_ping=True,
        )

        # Enable foreign key enforcement for SQLite (test environment)
        if url.startswith("sqlite"):
            @event.listens_for(_engine, "connect")
            def _set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Return a session factory bound to the current engine."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
