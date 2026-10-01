from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin

if TYPE_CHECKING:
    from app.db.models.delivery import Delivery


class DeliveryDocument(SoftDeleteMixin, Base):
    __tablename__ = "delivery_documents"
    __table_args__ = (
        Index("ix_delivery_documents_delivery_id", "delivery_id"),
        Index("ix_delivery_documents_deleted_at", "deleted_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    delivery_id: Mapped[int] = mapped_column(ForeignKey("deliveries.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    blob_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    delivery: Mapped["Delivery"] = relationship(back_populates="documents")
