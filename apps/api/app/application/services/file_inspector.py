"""File inspector for CSV and XLSX file structure, header, and row count validation."""

import csv
import io
from dataclasses import dataclass, field

import openpyxl


@dataclass(frozen=True)
class FileInspectionResult:
    """Result of inspecting an uploaded file."""

    is_valid: bool
    total_rows: int
    headers: list[str] = field(default_factory=list)
    error_message: str | None = None


class FileInspector:
    """Inspects uploaded files to extract row count, headers, and validate structure."""

    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

    @classmethod
    def inspect_file(cls, content: bytes, filename: str) -> FileInspectionResult:
        """Inspect file content based on extension (.csv or .xlsx)."""
        if len(content) > cls.MAX_FILE_SIZE_BYTES:
            max_mb = cls.MAX_FILE_SIZE_BYTES // (1024 * 1024)
            return FileInspectionResult(
                is_valid=False,
                total_rows=0,
                headers=[],
                error_message=f"File exceeds maximum size limit of {max_mb}MB.",
            )

        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if ext == "csv":
            return cls._inspect_csv(content)
        elif ext == "xlsx":
            return cls._inspect_xlsx(content)
        else:
            return FileInspectionResult(
                is_valid=False,
                total_rows=0,
                headers=[],
                error_message=f"Unsupported file extension: .{ext}",
            )

    @classmethod
    def _inspect_csv(cls, content: bytes) -> FileInspectionResult:
        """Inspect CSV byte stream."""
        try:
            try:
                text = content.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = content.decode("latin-1")

            lines = text.splitlines()
            if not lines:
                return FileInspectionResult(
                    is_valid=False,
                    total_rows=0,
                    headers=[],
                    error_message="File is empty.",
                )

            reader = csv.reader(lines)
            rows = list(reader)

            if not rows:
                return FileInspectionResult(
                    is_valid=False,
                    total_rows=0,
                    headers=[],
                    error_message="CSV contains no rows.",
                )

            headers = [str(h).strip() for h in rows[0]]
            data_rows = [r for r in rows[1:] if any(cell.strip() for cell in r)]
            total_rows = len(data_rows)

            return FileInspectionResult(
                is_valid=True,
                total_rows=total_rows,
                headers=headers,
            )
        except Exception as exc:
            return FileInspectionResult(
                is_valid=False,
                total_rows=0,
                headers=[],
                error_message=f"Failed to parse CSV file: {exc}",
            )

    @classmethod
    def _inspect_xlsx(cls, content: bytes) -> FileInspectionResult:
        """Inspect XLSX byte stream using openpyxl."""
        try:
            wb = openpyxl.load_workbook(
                filename=io.BytesIO(content), read_only=True, data_only=True
            )
            sheet = wb.active
            if sheet is None:
                return FileInspectionResult(
                    is_valid=False,
                    total_rows=0,
                    headers=[],
                    error_message="Excel workbook has no active sheet.",
                )

            rows_iter = sheet.iter_rows(values_only=True)
            try:
                first_row = next(rows_iter)
            except StopIteration:
                return FileInspectionResult(
                    is_valid=False,
                    total_rows=0,
                    headers=[],
                    error_message="Excel sheet is empty.",
                )

            headers = [str(cell).strip() if cell is not None else "" for cell in first_row]

            data_row_count = 0
            for row in rows_iter:
                if any(cell is not None and str(cell).strip() != "" for cell in row):
                    data_row_count += 1

            wb.close()

            return FileInspectionResult(
                is_valid=True,
                total_rows=data_row_count,
                headers=headers,
            )
        except Exception as exc:
            return FileInspectionResult(
                is_valid=False,
                total_rows=0,
                headers=[],
                error_message=f"Failed to parse XLSX file: {exc}",
            )
