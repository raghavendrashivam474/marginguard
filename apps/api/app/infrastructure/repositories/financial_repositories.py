"""SQLAlchemy concrete repository adapters for Supplier, PurchaseOrder, Invoice, and Payment entities."""

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ports import (
    InvoiceRepository,
    PaymentRepository,
    PurchaseOrderRepository,
    SupplierRepository,
)
from app.domain.entities import Invoice, Payment, PurchaseOrder, Supplier
from app.infrastructure.models import (
    InvoiceModel,
    PaymentModel,
    PurchaseOrderModel,
    SupplierModel,
)


class SqlAlchemySupplierRepository(SupplierRepository):
    """Concrete SQLAlchemy implementation of SupplierRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get_by_id(self, supplier_id: UUID) -> Supplier | None:
        model = self._session.get(SupplierModel, supplier_id)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_code(self, organization_id: UUID, code: str) -> Supplier | None:
        """Find supplier by external_reference within organization."""
        stmt = select(SupplierModel).where(
            SupplierModel.organization_id == organization_id,
            SupplierModel.external_reference == code,
        )
        model = self._session.scalars(stmt).first()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Supplier]:
        offset = (page - 1) * page_size
        stmt = (
            select(SupplierModel)
            .where(SupplierModel.organization_id == organization_id)
            .order_by(SupplierModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    async def save(
        self,
        supplier: Supplier,
        import_batch_id: UUID | None = None,
        source_row_number: int | None = None,
        original_data: dict | None = None,
    ) -> Supplier:
        model = self._session.get(SupplierModel, supplier.id)
        if model is None:
            model = SupplierModel(
                id=supplier.id,
                organization_id=supplier.organization_id,
                name=supplier.name,
                external_reference=supplier.external_reference,
                tax_identifier=supplier.tax_identifier,
                created_at=supplier.created_at,
                updated_at=supplier.updated_at,
                import_batch_id=import_batch_id,
                source_row_number=source_row_number,
                original_data=original_data,
            )
            self._session.add(model)
        else:
            model.name = supplier.name
            model.external_reference = supplier.external_reference
            model.tax_identifier = supplier.tax_identifier
            model.updated_at = supplier.updated_at
            if import_batch_id:
                model.import_batch_id = import_batch_id
            if source_row_number:
                model.source_row_number = source_row_number
            if original_data:
                model.original_data = original_data

        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: SupplierModel) -> Supplier:
        return Supplier(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
            external_reference=model.external_reference,
            tax_identifier=model.tax_identifier,
        )


class SqlAlchemyPurchaseOrderRepository(PurchaseOrderRepository):
    """Concrete SQLAlchemy implementation of PurchaseOrderRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get_by_id(self, po_id: UUID) -> PurchaseOrder | None:
        model = self._session.get(PurchaseOrderModel, po_id)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_number(self, organization_id: UUID, po_number: str) -> PurchaseOrder | None:
        """Find PO by external_reference within organization."""
        stmt = select(PurchaseOrderModel).where(
            PurchaseOrderModel.organization_id == organization_id,
            PurchaseOrderModel.external_reference == po_number,
        )
        model = self._session.scalars(stmt).first()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[PurchaseOrder]:
        offset = (page - 1) * page_size
        stmt = (
            select(PurchaseOrderModel)
            .where(PurchaseOrderModel.organization_id == organization_id)
            .order_by(PurchaseOrderModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    async def save(
        self,
        purchase_order: PurchaseOrder,
        import_batch_id: UUID | None = None,
        source_row_number: int | None = None,
        original_data: dict | None = None,
    ) -> PurchaseOrder:
        model = self._session.get(PurchaseOrderModel, purchase_order.id)
        if model is None:
            model = PurchaseOrderModel(
                id=purchase_order.id,
                organization_id=purchase_order.organization_id,
                supplier_id=purchase_order.supplier_id,
                external_reference=purchase_order.external_reference,
                order_date=purchase_order.order_date,
                currency=purchase_order.currency,
                total_amount=purchase_order.total_amount,
                status=purchase_order.status,
                created_at=purchase_order.created_at,
                import_batch_id=import_batch_id,
                source_row_number=source_row_number,
                original_data=original_data,
            )
            self._session.add(model)
        else:
            model.status = purchase_order.status
            model.total_amount = purchase_order.total_amount

        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: PurchaseOrderModel) -> PurchaseOrder:
        return PurchaseOrder(
            id=model.id,
            organization_id=model.organization_id,
            supplier_id=model.supplier_id,
            external_reference=model.external_reference,
            order_date=model.order_date,
            currency=model.currency,
            total_amount=model.total_amount,
            status=model.status,
            created_at=model.created_at,
        )


class SqlAlchemyInvoiceRepository(InvoiceRepository):
    """Concrete SQLAlchemy implementation of InvoiceRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        model = self._session.get(InvoiceModel, invoice_id)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_number(self, organization_id: UUID, invoice_number: str) -> Invoice | None:
        """Find invoice by external_reference within organization."""
        stmt = select(InvoiceModel).where(
            InvoiceModel.organization_id == organization_id,
            InvoiceModel.external_reference == invoice_number,
        )
        model = self._session.scalars(stmt).first()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Invoice]:
        offset = (page - 1) * page_size
        stmt = (
            select(InvoiceModel)
            .where(InvoiceModel.organization_id == organization_id)
            .order_by(InvoiceModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    async def save(
        self,
        invoice: Invoice,
        import_batch_id: UUID | None = None,
        source_row_number: int | None = None,
        original_data: dict | None = None,
    ) -> Invoice:
        model = self._session.get(InvoiceModel, invoice.id)
        if model is None:
            model = InvoiceModel(
                id=invoice.id,
                organization_id=invoice.organization_id,
                supplier_id=invoice.supplier_id,
                purchase_order_id=invoice.purchase_order_id,
                external_reference=invoice.external_reference,
                invoice_date=invoice.invoice_date,
                due_date=invoice.due_date,
                currency=invoice.currency,
                subtotal=invoice.subtotal,
                tax_amount=invoice.tax_amount,
                total_amount=invoice.total_amount,
                created_at=invoice.created_at,
                import_batch_id=import_batch_id,
                source_row_number=source_row_number,
                original_data=original_data,
            )
            self._session.add(model)
        else:
            model.due_date = invoice.due_date
            model.total_amount = invoice.total_amount

        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: InvoiceModel) -> Invoice:
        return Invoice(
            id=model.id,
            organization_id=model.organization_id,
            supplier_id=model.supplier_id,
            purchase_order_id=model.purchase_order_id,
            external_reference=model.external_reference,
            invoice_date=model.invoice_date,
            due_date=model.due_date,
            currency=model.currency,
            subtotal=model.subtotal,
            tax_amount=model.tax_amount,
            total_amount=model.total_amount,
            created_at=model.created_at,
        )


class SqlAlchemyPaymentRepository(PaymentRepository):
    """Concrete SQLAlchemy implementation of PaymentRepository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    async def get_by_id(self, payment_id: UUID) -> Payment | None:
        model = self._session.get(PaymentModel, payment_id)
        if model is None:
            return None
        return self._to_domain(model)

    def find_by_reference(self, organization_id: UUID, reference: str) -> Payment | None:
        """Find payment by external_reference within organization."""
        stmt = select(PaymentModel).where(
            PaymentModel.organization_id == organization_id,
            PaymentModel.external_reference == reference,
        )
        model = self._session.scalars(stmt).first()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_by_organization(
        self, organization_id: UUID, *, page: int = 1, page_size: int = 20
    ) -> list[Payment]:
        offset = (page - 1) * page_size
        stmt = (
            select(PaymentModel)
            .where(PaymentModel.organization_id == organization_id)
            .order_by(PaymentModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        models = self._session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    async def save(
        self,
        payment: Payment,
        import_batch_id: UUID | None = None,
        source_row_number: int | None = None,
        original_data: dict | None = None,
    ) -> Payment:
        model = self._session.get(PaymentModel, payment.id)
        if model is None:
            model = PaymentModel(
                id=payment.id,
                organization_id=payment.organization_id,
                supplier_id=payment.supplier_id,
                external_reference=payment.external_reference,
                payment_date=payment.payment_date,
                currency=payment.currency,
                amount=payment.amount,
                payment_method=payment.payment_method,
                created_at=payment.created_at,
                import_batch_id=import_batch_id,
                source_row_number=source_row_number,
                original_data=original_data,
            )
            self._session.add(model)
        else:
            model.amount = payment.amount

        self._session.commit()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            organization_id=model.organization_id,
            supplier_id=model.supplier_id,
            external_reference=model.external_reference,
            payment_date=model.payment_date,
            currency=model.currency,
            amount=model.amount,
            payment_method=model.payment_method,
            created_at=model.created_at,
        )
