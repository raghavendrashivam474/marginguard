"""Unit tests for CsvRowReader."""

from app.application.services.csv_reader import CsvRowReader


def test_csv_reader_basic():
    csv_bytes = b"supplier_code,supplier_name\nSUPP-001,Acme Corp\nSUPP-002,Global Logistics\n"
    rows = list(CsvRowReader.read_bytes(csv_bytes))

    assert len(rows) == 2
    assert rows[0].source_row_number == 2
    assert rows[0].data == {"supplier_code": "SUPP-001", "supplier_name": "Acme Corp"}
    assert rows[1].source_row_number == 3
    assert rows[1].data == {"supplier_code": "SUPP-002", "supplier_name": "Global Logistics"}


def test_csv_reader_with_utf8_bom():
    # Byte order mark for UTF-8 (\xef\xbb\xbf)
    csv_bytes = "\ufeffpo_number,amount\nPO-100,500.00\n".encode("utf-8")
    rows = list(CsvRowReader.read_bytes(csv_bytes))

    assert len(rows) == 1
    assert "po_number" in rows[0].data
    assert rows[0].data["po_number"] == "PO-100"


def test_csv_reader_handles_quoted_commas():
    csv_bytes = b'invoice_number,supplier_name,total_amount\nINV-01,"Smith, Jones & Co",1500.00\n'
    rows = list(CsvRowReader.read_bytes(csv_bytes))

    assert len(rows) == 1
    assert rows[0].data["supplier_name"] == "Smith, Jones & Co"
    assert rows[0].data["total_amount"] == "1500.00"


def test_csv_reader_skips_empty_lines():
    csv_bytes = b"code,name\n\nC1,Name 1\n   \n\nC2,Name 2\n"
    rows = list(CsvRowReader.read_bytes(csv_bytes))

    assert len(rows) == 2
    assert rows[0].source_row_number == 3
    assert rows[0].data["code"] == "C1"
    assert rows[1].source_row_number == 6
    assert rows[1].data["code"] == "C2"
