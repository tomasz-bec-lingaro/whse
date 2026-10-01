from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.api import openapi_examples as examples
from app.db.models import Delivery, Supplier, Warehouse
from app.db.session import get_db
from app.domain.enums import DeliveryStatus
from app.schemas.common import PaginatedResponse
from app.schemas.deliveries import (
    DeliveryCreate,
    DeliveryRead,
    DeliveryStatusUpdate,
    DeliveryUpdate,
)
from app.services.delivery_status import is_transition_allowed

router = APIRouter()


def _get_delivery_or_404(delivery_id: int, db: Session) -> Delivery:
    delivery = db.scalar(
        select(Delivery).where(Delivery.id == delivery_id, Delivery.deleted_at.is_(None))
    )
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    return delivery


def _ensure_related_entities_exist(payload: DeliveryCreate | DeliveryUpdate, db: Session) -> None:
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


@router.post(
    "",
    response_model=DeliveryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create delivery",
    description="Creates a warehouse delivery assigned to an existing supplier and warehouse.",
    response_description="Created delivery.",
    responses={
        201: {"content": {"application/json": {"example": examples.DELIVERY_RESPONSE}}},
        400: {"content": {"application/json": {"example": {"detail": "Supplier does not exist."}}}},
    },
)
def create_delivery(payload: DeliveryCreate, db: Session = Depends(get_db)) -> Delivery:
    _ensure_related_entities_exist(payload, db)
    delivery = Delivery(**payload.model_dump())
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


@router.get(
    "",
    response_model=PaginatedResponse[DeliveryRead],
    summary="List deliveries",
    description=(
        "Returns deliveries with pagination and optional filtering by supplier, warehouse, "
        "status, and delivery date range."
    ),
    response_description="Paginated deliveries list.",
    responses={
        200: {"content": {"application/json": {"example": examples.DELIVERIES_PAGE_RESPONSE}}}
    },
)
def list_deliveries(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    supplier_id: int | None = None,
    warehouse_id: int | None = None,
    status_filter: DeliveryStatus | None = Query(default=None, alias="status"),
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
) -> PaginatedResponse[DeliveryRead]:
    conditions = [Delivery.deleted_at.is_(None)]

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

    base_query: Select[tuple[Delivery]] = select(Delivery).where(*conditions)
    total = db.scalar(select(func.count()).select_from(Delivery).where(*conditions)) or 0
    items = db.scalars(
        base_query.order_by(Delivery.delivery_date.desc(), Delivery.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return PaginatedResponse[DeliveryRead](items=items, page=page, size=size, total=total)


@router.get(
    "/{delivery_id}",
    response_model=DeliveryRead,
    summary="Get delivery",
    description="Returns a single active delivery by ID.",
    response_description="Delivery details.",
    responses={
        200: {"content": {"application/json": {"example": examples.DELIVERY_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
    },
)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)) -> Delivery:
    return _get_delivery_or_404(delivery_id, db)


@router.put(
    "/{delivery_id}",
    response_model=DeliveryRead,
    summary="Update delivery",
    description="Updates delivery assignment, date, or status when the transition is allowed.",
    response_description="Updated delivery.",
    responses={
        200: {"content": {"application/json": {"example": examples.DELIVERY_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
        409: {"content": {"application/json": {"example": examples.INVALID_TRANSITION_RESPONSE}}},
    },
)
def update_delivery(
    delivery_id: int,
    payload: DeliveryUpdate,
    db: Session = Depends(get_db),
) -> Delivery:
    _ensure_related_entities_exist(payload, db)
    delivery = _get_delivery_or_404(delivery_id, db)
    updates = payload.model_dump(exclude_unset=True)

    if "status" in updates and not is_transition_allowed(delivery.status, updates["status"]):
        raise HTTPException(status_code=409, detail="Delivery status transition is not allowed.")

    for field, value in updates.items():
        setattr(delivery, field, value)
    db.commit()
    db.refresh(delivery)
    return delivery


@router.patch(
    "/{delivery_id}/status",
    response_model=DeliveryRead,
    summary="Update delivery status",
    description="Changes delivery status using the allowed lifecycle transitions.",
    response_description="Delivery with updated status.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        **examples.DELIVERY_RESPONSE,
                        "status": "RECEIVED",
                        "updated_at": "2026-10-01T11:00:00Z",
                    }
                }
            }
        },
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
        409: {"content": {"application/json": {"example": examples.INVALID_TRANSITION_RESPONSE}}},
    },
)
def update_delivery_status(
    delivery_id: int,
    payload: DeliveryStatusUpdate,
    db: Session = Depends(get_db),
) -> Delivery:
    delivery = _get_delivery_or_404(delivery_id, db)
    if not is_transition_allowed(delivery.status, payload.status):
        raise HTTPException(status_code=409, detail="Delivery status transition is not allowed.")
    delivery.status = payload.status
    db.commit()
    db.refresh(delivery)
    return delivery


@router.delete(
    "/{delivery_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete delivery",
    description="Marks a delivery as deleted without removing the database record.",
    response_description="Delivery deleted.",
    responses={404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}}},
)
def delete_delivery(delivery_id: int, db: Session = Depends(get_db)) -> None:
    delivery = _get_delivery_or_404(delivery_id, db)
    delivery.deleted_at = datetime.now(UTC)
    db.commit()
