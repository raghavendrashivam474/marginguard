"""Local filesystem storage implementation for uploaded files."""

import hashlib
import uuid
from pathlib import Path

from app.infrastructure.storage.base import StoragePort, StoredFileResult


class LocalFileStorageService(StoragePort):
    """Local disk storage with SHA-256 checksums and tenant isolation."""

    def __init__(self, base_dir: str | Path = "data/uploads") -> None:
        self._base_dir = Path(base_dir).resolve()
        self._base_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self,
        organization_id_str: str,
        filename: str,
        content: bytes,
    ) -> StoredFileResult:
        """Persist file to disk under organization directory with UUID storage key."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        safe_ext = f".{ext}" if ext else ""
        file_uuid = uuid.uuid4().hex

        rel_key = f"{organization_id_str}/{file_uuid}{safe_ext}"
        full_path = self._base_dir / organization_id_str / f"{file_uuid}{safe_ext}"

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(content)

        checksum = hashlib.sha256(content).hexdigest()

        return StoredFileResult(
            storage_key=rel_key,
            file_path=full_path,
            filename=filename,
            file_size=len(content),
            checksum_sha256=checksum,
        )

    async def get_file_path(self, storage_key: str) -> Path | None:
        """Resolve storage key to absolute file path preventing path traversal."""
        path = (self._base_dir / storage_key).resolve()
        if not path.is_relative_to(self._base_dir) or not path.exists():
            return None
        return path


# Alias for backward compatibility
LocalStorageAdapter = LocalFileStorageService
