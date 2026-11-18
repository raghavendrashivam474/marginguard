"""add provenance columns and batch metadata

Revision ID: 6d8e9f01a2b3
Revises: 5c0df3e49454
Create Date: 2026-11-16 00:00:00.000000+00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6d8e9f01a2b3"
down_revision: Union[str, None] = "5c0df3e49454"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. import_batches metadata columns
    op.add_column("import_batches", sa.Column("file_hash", sa.String(length=64), nullable=True))
    op.add_column("import_batches", sa.Column("storage_key", sa.String(length=500), nullable=True))
    op.add_column("import_batches", sa.Column("error_summary", sa.JSON(), nullable=True))

    # 2. suppliers provenance columns
    op.add_column("suppliers", sa.Column("import_batch_id", sa.UUID(), nullable=True))
    op.add_column("suppliers", sa.Column("source_row_number", sa.Integer(), nullable=True))
    op.add_column("suppliers", sa.Column("original_data", sa.JSON(), nullable=True))
    op.create_foreign_key(
        "fk_suppliers_import_batch_id",
        "suppliers",
        "import_batches",
        ["import_batch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_suppliers_import_batch_id", "suppliers", ["import_batch_id"], unique=False)

    # 3. purchase_orders provenance columns
    op.add_column("purchase_orders", sa.Column("import_batch_id", sa.UUID(), nullable=True))
    op.add_column("purchase_orders", sa.Column("source_row_number", sa.Integer(), nullable=True))
    op.add_column("purchase_orders", sa.Column("original_data", sa.JSON(), nullable=True))
    op.create_foreign_key(
        "fk_purchase_orders_import_batch_id",
        "purchase_orders",
        "import_batches",
        ["import_batch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_purchase_orders_import_batch_id", "purchase_orders", ["import_batch_id"], unique=False
    )

    # 4. invoices provenance columns
    op.add_column("invoices", sa.Column("import_batch_id", sa.UUID(), nullable=True))
    op.add_column("invoices", sa.Column("source_row_number", sa.Integer(), nullable=True))
    op.add_column("invoices", sa.Column("original_data", sa.JSON(), nullable=True))
    op.create_foreign_key(
        "fk_invoices_import_batch_id",
        "invoices",
        "import_batches",
        ["import_batch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_invoices_import_batch_id", "invoices", ["import_batch_id"], unique=False)

    # 5. payments provenance columns
    op.add_column("payments", sa.Column("import_batch_id", sa.UUID(), nullable=True))
    op.add_column("payments", sa.Column("source_row_number", sa.Integer(), nullable=True))
    op.add_column("payments", sa.Column("original_data", sa.JSON(), nullable=True))
    op.create_foreign_key(
        "fk_payments_import_batch_id",
        "payments",
        "import_batches",
        ["import_batch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_payments_import_batch_id", "payments", ["import_batch_id"], unique=False)


def downgrade() -> None:
    # 5. payments
    op.drop_index("ix_payments_import_batch_id", table_name="payments")
    op.drop_constraint("fk_payments_import_batch_id", "payments", type_="foreignkey")
    op.drop_column("payments", "original_data")
    op.drop_column("payments", "source_row_number")
    op.drop_column("payments", "import_batch_id")

    # 4. invoices
    op.drop_index("ix_invoices_import_batch_id", table_name="invoices")
    op.drop_constraint("fk_invoices_import_batch_id", "invoices", type_="foreignkey")
    op.drop_column("invoices", "original_data")
    op.drop_column("invoices", "source_row_number")
    op.drop_column("invoices", "import_batch_id")

    # 3. purchase_orders
    op.drop_index("ix_purchase_orders_import_batch_id", table_name="purchase_orders")
    op.drop_constraint("fk_purchase_orders_import_batch_id", "purchase_orders", type_="foreignkey")
    op.drop_column("purchase_orders", "original_data")
    op.drop_column("purchase_orders", "source_row_number")
    op.drop_column("purchase_orders", "import_batch_id")

    # 2. suppliers
    op.drop_index("ix_suppliers_import_batch_id", table_name="suppliers")
    op.drop_constraint("fk_suppliers_import_batch_id", "suppliers", type_="foreignkey")
    op.drop_column("suppliers", "original_data")
    op.drop_column("suppliers", "source_row_number")
    op.drop_column("suppliers", "import_batch_id")

    # 1. import_batches
    op.drop_column("import_batches", "error_summary")
    op.drop_column("import_batches", "storage_key")
    op.drop_column("import_batches", "file_hash")
