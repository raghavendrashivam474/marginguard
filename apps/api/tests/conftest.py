"""Pytest fixtures and test environment configuration."""

import os
import tempfile
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set test environment database URL prior to app imports
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg2://marginguard:marginguard_dev_2025@127.0.0.1:15432/marginguard"
)

from app.api.dependencies import get_storage_service  # noqa: E402
from app.infrastructure.storage.local_storage import LocalFileStorageService  # noqa: E402
from app.main import app  # noqa: E402

# Create a temporary directory for test file uploads
TEST_STORAGE_DIR = os.path.join(
    tempfile.gettempdir(), f"marginguard_test_storage_{uuid.uuid4().hex}"
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure storage directory exists before tests run."""
    os.makedirs(TEST_STORAGE_DIR, exist_ok=True)
    yield


@pytest.fixture
def override_storage():
    """Provide isolated storage service pointing to test storage dir."""
    return LocalFileStorageService(base_dir=TEST_STORAGE_DIR)


@pytest_asyncio.fixture
async def client(override_storage):
    """Provide an HTTPX AsyncClient with storage dependency overridden."""
    app.dependency_overrides[get_storage_service] = lambda: override_storage

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
