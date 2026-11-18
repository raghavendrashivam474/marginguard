"""Streaming CSV row reader adapter with encoding detection and raw line index tracking."""

import csv
from dataclasses import dataclass
from typing import Any, Iterator, Sequence


@dataclass(frozen=True, slots=True)
class ParsedCsvRow:
    """Structured representation of a single physical CSV row."""

    source_row_number: int  # 1-based physical line index in file (row 1 is header)
    data: dict[str, str]  # Cleaned header -> raw string value mapping
    raw_values: Sequence[str]  # Positional cell values
    original_data: dict[str, Any]  # Raw JSON-serializable dictionary snapshot


class CsvRowReader:
    """Streaming CSV row reader supporting utf-8-sig BOM handling and line index tracking."""

    @classmethod
    def read_bytes(cls, content: bytes) -> Iterator[ParsedCsvRow]:
        """Parse byte stream row by row yielding ParsedCsvRow objects."""
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = content.decode("latin-1")

        lines = text.splitlines()
        if not lines:
            return

        reader = csv.reader(lines)

        try:
            header_row = next(reader)
        except StopIteration:
            return

        headers = [str(h).strip().lower() for h in header_row]

        physical_row = 1  # Header row index

        for raw_cells in reader:
            physical_row += 1

            # Skip empty lines (all cells whitespace or empty)
            if not any(cell and cell.strip() for cell in raw_cells):
                continue

            row_dict: dict[str, str] = {}
            for idx, header_name in enumerate(headers):
                if not header_name:
                    continue
                cell_val = raw_cells[idx].strip() if idx < len(raw_cells) else ""
                row_dict[header_name] = cell_val

            yield ParsedCsvRow(
                source_row_number=physical_row,
                data=row_dict,
                raw_values=[c.strip() for c in raw_cells],
                original_data=dict(row_dict),
            )
