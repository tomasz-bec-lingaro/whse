from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin
from app.domain.enums import DeliveryStatus

if TYPE_CHECKING:
    from app.db.models.delivery_document import DeliveryDocument
    from app.db.models.supplier import Supplier
    from app.db.models.warehouse import Warehouse


class Delivery(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "deliveries"
    __table_args__ = (
        Index("ix_deliveries_supplier_id", "supplier_id"),
        Index("ix_deliveries_warehouse_id", "warehouse_id"),
        Index("ix_deliveries_delivery_date", "delivery_date"),
        Index("ix_deliveries_status", "status"),
        Index("ix_deliveries_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=False)
    delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status", native_enum=False),
        default=DeliveryStatus.CREATED,
        nullable=False,
    )

    supplier: Mapped["Supplier"] = relationship(back_populates="deliveries")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="deliveries")
    documents: Mapped[list["DeliveryDocument"]] = relationship(back_populates="delivery")
