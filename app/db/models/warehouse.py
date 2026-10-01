from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from app.db.models.delivery import Delivery


class Warehouse(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        UniqueConstraint("code", name="uq_warehouses_code"),
        Index("ix_warehouses_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    deliveries: Mapped[list["Delivery"]] = relationship(back_populates="warehouse")
