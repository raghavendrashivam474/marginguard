"""MarginGuard infrastructure — Storage interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StoredFileResult:
    """Metadata describing a stored source file."""

    storage_key: str
    file_path: Path
    filename: str
    file_size: int
    checksum_sha256: str


class StoragePort(ABC):
    """Abstract interface for file storage implementations."""

    @abstractmethod
    async def save_file(
        self,
        organization_id_str: str,
        filename: str,
        content: bytes,
    ) -> StoredFileResult: ...

    @abstractmethod
    async def get_file_path(self, storage_key: str) -> Path | None: ...
