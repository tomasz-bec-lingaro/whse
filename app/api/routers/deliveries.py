from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.api import openapi_examples as examples
from app.db.models import Delivery
from app.db.session import get_db
from app.domain.enums import DeliveryStatus
from app.schemas.common import PaginatedResponse
from app.schemas.deliveries import (
    DeliveryCreate,
    DeliveryRead,
    DeliveryStatusUpdate,
    DeliveryUpdate,
)
from app.services.deliveries import (
    build_delivery_filters,
    ensure_related_entities_exist,
    ensure_status_transition_allowed,
    get_delivery_or_404,
)

router = APIRouter()


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
    ensure_related_entities_exist(payload, db)
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
    conditions = build_delivery_filters(
        supplier_id,
        warehouse_id,
        status_filter,
        date_from,
        date_to,
    )

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
    return get_delivery_or_404(delivery_id, db)


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
    ensure_related_entities_exist(payload, db)
    delivery = get_delivery_or_404(delivery_id, db)
    updates = payload.model_dump(exclude_unset=True)

    if "status" in updates:
        ensure_status_transition_allowed(delivery, updates["status"])

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
    delivery = get_delivery_or_404(delivery_id, db)
    ensure_status_transition_allowed(delivery, payload.status)
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
    delivery = get_delivery_or_404(delivery_id, db)
    delivery.deleted_at = datetime.now(UTC)
    db.commit()
