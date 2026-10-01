"""Initial WHS delivery schema."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261001_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tax_id", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tax_id", name="uq_suppliers_tax_id"),
    )
    op.create_index("ix_suppliers_deleted_at", "suppliers", ["deleted_at"])

    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("code", name="uq_warehouses_code"),
    )
    op.create_index("ix_warehouses_deleted_at", "warehouses", ["deleted_at"])

    op.create_table(
        "deliveries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="CREATED"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
    )
    op.create_index("ix_deliveries_supplier_id", "deliveries", ["supplier_id"])
    op.create_index("ix_deliveries_warehouse_id", "deliveries", ["warehouse_id"])
    op.create_index("ix_deliveries_delivery_date", "deliveries", ["delivery_date"])
    op.create_index("ix_deliveries_status", "deliveries", ["status"])
    op.create_index("ix_deliveries_deleted_at", "deliveries", ["deleted_at"])

    op.create_table(
        "delivery_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("delivery_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("blob_path", sa.String(length=1024), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column(
            "uploaded_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["delivery_id"], ["deliveries.id"]),
    )
    op.create_index("ix_delivery_documents_delivery_id", "delivery_documents", ["delivery_id"])
    op.create_index("ix_delivery_documents_deleted_at", "delivery_documents", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_delivery_documents_deleted_at", table_name="delivery_documents")
    op.drop_index("ix_delivery_documents_delivery_id", table_name="delivery_documents")
    op.drop_table("delivery_documents")

    op.drop_index("ix_deliveries_deleted_at", table_name="deliveries")
    op.drop_index("ix_deliveries_status", table_name="deliveries")
    op.drop_index("ix_deliveries_delivery_date", table_name="deliveries")
    op.drop_index("ix_deliveries_warehouse_id", table_name="deliveries")
    op.drop_index("ix_deliveries_supplier_id", table_name="deliveries")
    op.drop_table("deliveries")

    op.drop_index("ix_warehouses_deleted_at", table_name="warehouses")
    op.drop_table("warehouses")

    op.drop_index("ix_suppliers_deleted_at", table_name="suppliers")
    op.drop_table("suppliers")
