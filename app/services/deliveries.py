from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Delivery, Supplier, Warehouse
from app.domain.enums import DeliveryStatus
from app.schemas.deliveries import DeliveryCreate, DeliveryUpdate
from app.services.delivery_status import is_transition_allowed


def get_delivery_or_404(delivery_id: int, db: Session) -> Delivery:
    delivery = db.scalar(
        select(Delivery).where(Delivery.id == delivery_id, Delivery.deleted_at.is_(None))
    )
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    return delivery


def ensure_related_entities_exist(payload: DeliveryCreate | DeliveryUpdate, db: Session) -> None:
    values = payload.model_dump(exclude_unset=True)
    supplier_id = values.get("supplier_id")
    warehouse_id = values.get("warehouse_id")

    if supplier_id is not None:
        supplier_exists = db.scalar(
            select(Supplier.id).where(Supplier.id == supplier_id, Supplier.deleted_at.is_(None))
        )
        if supplier_exists is None:
            raise HTTPException(status_code=400, detail="Supplier does not exist.")

    if warehouse_id is not None:
        warehouse_exists = db.scalar(
            select(Warehouse.id).where(
                Warehouse.id == warehouse_id,
                Warehouse.deleted_at.is_(None),
            )
        )
        if warehouse_exists is None:
            raise HTTPException(status_code=400, detail="Warehouse does not exist.")


def build_delivery_filters(
    supplier_id: int | None,
    warehouse_id: int | None,
    status_filter: DeliveryStatus | None,
    date_from: date | None,
    date_to: date | None,
) -> list[object]:
    conditions: list[object] = [Delivery.deleted_at.is_(None)]

    if supplier_id is not None:
        conditions.append(Delivery.supplier_id == supplier_id)
    if warehouse_id is not None:
        conditions.append(Delivery.warehouse_id == warehouse_id)
    if status_filter is not None:
        conditions.append(Delivery.status == status_filter)
    if date_from is not None:
        conditions.append(Delivery.delivery_date >= date_from)
    if date_to is not None:
        conditions.append(Delivery.delivery_date <= date_to)

    return conditions


def ensure_status_transition_allowed(delivery: Delivery, target_status: DeliveryStatus) -> None:
    if not is_transition_allowed(delivery.status, target_status):
        raise HTTPException(status_code=409, detail="Delivery status transition is not allowed.")
