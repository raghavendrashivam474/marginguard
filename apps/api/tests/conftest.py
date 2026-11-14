"""MarginGuard test configuration.

Provides shared fixtures for all backend tests.
Uses SQLite in-memory for speed (documented exception per ADR-005).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client for HTTP-level tests."""
    return TestClient(app)
