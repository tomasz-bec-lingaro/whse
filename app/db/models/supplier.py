from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.delivery import Delivery


class Supplier(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "suppliers"
    __table_args__ = (
        UniqueConstraint("tax_id", name="uq_suppliers_tax_id"),
        Index("ix_suppliers_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)

    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="supplier")
