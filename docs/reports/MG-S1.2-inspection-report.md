# MG-S1.2 — Technical Repository Inspection Report

**Sprint ID:** MG-S1.2  
**Date:** 2026-11-18  
**Baseline Commit:** f75d4cb (tag: v-MG-S1.1)  
**Branch:** feature/mg-s1.2-row-ingestion  

---

## 1. Existing Upload Execution Flow

The existing file upload flow in -MG-S1.1 operates as follows:

1. **Endpoint:** POST /api/v1/organizations/{organization_id}/imports (pp/api/v1/org_imports.py)
2. **Ingestion Orchestration:** IngestionService.ingest_file(...) (pp/application/services/ingestion_service.py)
   - Invokes FileInspector.inspect_file(content, filename) to validate max file size (50 MB), extension (.csv / .xlsx), and count non-empty data rows.
   - Resolves or creates a DataSource entity via DataSourceRepository.find_or_create(...).
   - Persists uploaded bytes to local disk using LocalFileStorageService.save_file(...) under data/uploads/{org_id}/{file_uuid}.{ext}.
   - Calculates SHA-256 file checksum and relative storage_key.
   - Creates an ImportBatch domain entity.
   - Persists the batch via SqlAlchemyImportBatchRepository.save(...).
3. **Current Outcome:** In -MG-S1.1, the upload completed with status = ImportStatus.COMPLETED immediately after file inspection and storage, with 	otal_rows = N, successful_rows = 0, and ailed_rows = 0. No row-level parsing or domain entity persistence was performed.

---

## 2. Existing ImportBatch Lifecycle & Status Transitions

- **Domain Enum (ImportStatus):** PENDING, PROCESSING, COMPLETED, PARTIALLY_COMPLETED, FAILED.
- **Database Constraint (ck_import_batches_status):** status IN ('pending', 'processing', 'completed', 'partially_completed', 'failed').
- **Target Ingestion Lifecycle for MG-S1.2:**
  - PENDING -> Upload received & stored, awaiting row parsing.
  - PROCESSING -> Ingestion engine actively parsing, validating, and mapping rows.
  - COMPLETED -> All rows parsed and persisted with 0 failures.
  - PARTIALLY_COMPLETED -> Ingestion finished with a mix of accepted rows and recorded rejections.
  - FAILED -> Fatal processing or file verification error.

---

## 3. Actual Fields Available in Canonical Domain Entities

The core financial domain entities in pp/domain/entities.py define the following fields:

1. **Supplier**
   - id: UUID, organization_id: UUID, 
ame: str, created_at: datetime, updated_at: datetime, external_reference: str | None, 	ax_identifier: str | None.
2. **PurchaseOrder**
   - id: UUID, organization_id: UUID, supplier_id: UUID, external_reference: str, order_date: date, currency: str, 	otal_amount: Decimal, status: str, created_at: datetime.
3. **Invoice**
   - id: UUID, organization_id: UUID, supplier_id: UUID, external_reference: str, invoice_date: date, currency: str, subtotal: Decimal, 	ax_amount: Decimal, 	otal_amount: Decimal, created_at: datetime, purchase_order_id: UUID | None, due_date: date | None.
   - *Domain Invariant:* 	otal_amount == subtotal + tax_amount (raises ValueError on mismatch).
4. **Payment**
   - id: UUID, organization_id: UUID, payment_date: date, currency: str, mount: Decimal, created_at: datetime, supplier_id: UUID | None, external_reference: str | None, payment_method: str | None.
   - *Domain Invariant:* mount > 0 (raises ValueError if non-positive).

---

## 4. Existing Repository Methods & Adapters

- **Defined Ports (pp/application/ports.py):**
  - OrganizationRepository: get_by_id, list_all, save.
  - DataSourceRepository: get_by_id, list_by_organization, save.
  - ImportBatchRepository: get_by_id, list_by_organization, save, update_status.
  - SupplierRepository, PurchaseOrderRepository, InvoiceRepository, PaymentRepository: Defined as abstract interfaces in ports.py.
- **Existing Concrete Adapters (pp/infrastructure/repositories/):**
  - SqlAlchemyOrganizationRepository
  - SqlAlchemyDataSourceRepository
  - SqlAlchemyImportBatchRepository
- **Gaps Identified:** Concrete SQLAlchemy implementations for SupplierRepository, PurchaseOrderRepository, InvoiceRepository, and PaymentRepository do not yet exist in pp/infrastructure/repositories/ and must be built in this sprint.

---

## 5. Existing Database Schema & ORM Alignment Gaps

Inspection revealed minor column naming discrepancies between SQLAlchemy ORM models (pp/infrastructure/models.py) and the Alembic initial migration (migrations/versions/20261115_1904...):

1. **PurchaseOrderModel vs purchase_orders Table:**
   - Model uses po_number: Mapped[str] while initial migration created external_reference.
2. **InvoiceModel vs invoices Table:**
   - Model uses invoice_number and subtotal_amount while initial migration created external_reference and subtotal.
3. **PaymentModel vs payments Table:**
   - Model uses payment_number while initial migration created external_reference.

*Action Plan:* Align mapped column names in pp/infrastructure/models.py with the existing database schema (external_reference, subtotal) without modifying the immutable initial migration file.

---

## 6. ADR-007 Provenance Requirements

ADR-007 mandates that every imported canonical record must carry:
1. import_batch_id (FK -> import_batches.id)
2. source_row_number (Integer, 1-based index)
3. original_data (JSONB snapshot of the raw imported CSV row)

Currently, suppliers, purchase_orders, invoices, and payments tables and ORM models do not have these three provenance columns. As specified in ADR-007, an additive Alembic migration (20261116_0000_add_provenance_columns.py) will be created in Stage S2.

---

## 7. Required Sprint Capabilities (Scope Breakdown)

1. **Additive Schema Revision:** Add import_batch_id, source_row_number, and original_data to financial tables and ORM models.
2. **Concrete Repositories:** Implement SqlAlchemySupplierRepository, SqlAlchemyPurchaseOrderRepository, SqlAlchemyInvoiceRepository, and SqlAlchemyPaymentRepository.
3. **Row Reader:** Implement efficient streaming/iterator-based CSV row reading with BOM handling (utf-8-sig) and raw line index tracking.
4. **Canonical Templates & Mappers:** Standardized CSV mappings for Suppliers, Purchase Orders, Invoices, and Payments with strict Decimal monetary handling and domain validation.
5. **Row Validation & Error Handling:** Structured error reporting (source_row_number, ield_name, error_code, message).
6. **Import Lifecycle & Retry / Idempotency:** Update ImportBatch status and counters (	otal_rows, successful_rows, ailed_rows). Prevent duplicate record insertion on re-processing.
7. **API Verification:** Ensure endpoints expose batch processing summaries and details.

---

## 8. Summary of Planned Additive Changes

- **Schema:** New additive Alembic migration for provenance columns (no changes to existing initial migration).
- **Models:** Add provenance mapped columns to ORM models & fix mapped column name aliases.
- **Repositories:** Add concrete financial repository adapters.
- **Application Services:** Add CSV row reader, mappers, validators, and row-level ingestion orchestration.
