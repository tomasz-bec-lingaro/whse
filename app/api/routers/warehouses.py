from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api import openapi_examples as examples
from app.db.models import Warehouse
from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.warehouses import WarehouseCreate, WarehouseRead, WarehouseUpdate

router = APIRouter()


@router.post(
    "",
    response_model=WarehouseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create warehouse",
    description="Creates a warehouse that can receive deliveries.",
    response_description="Created warehouse.",
    responses={
        201: {"content": {"application/json": {"example": examples.WAREHOUSE_RESPONSE}}},
        409: {"content": {"application/json": {"example": examples.CONFLICT_RESPONSE}}},
    },
)
def create_warehouse(payload: WarehouseCreate, db: Session = Depends(get_db)) -> Warehouse:
    warehouse = Warehouse(**payload.model_dump())
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.get(
    "",
    response_model=PaginatedResponse[WarehouseRead],
    summary="List warehouses",
    description="Returns active warehouses with page-based pagination.",
    response_description="Paginated warehouses list.",
    responses={
        200: {"content": {"application/json": {"example": examples.WAREHOUSES_PAGE_RESPONSE}}}
    },
)
def list_warehouses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[WarehouseRead]:
    filters = Warehouse.deleted_at.is_(None)
    total = db.scalar(select(func.count()).select_from(Warehouse).where(filters)) or 0
    items = db.scalars(
        select(Warehouse)
        .where(filters)
        .order_by(Warehouse.id)
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return PaginatedResponse[WarehouseRead](items=items, page=page, size=size, total=total)


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    summary="Get warehouse",
    description="Returns a single active warehouse by ID.",
    response_description="Warehouse details.",
    responses={
        200: {"content": {"application/json": {"example": examples.WAREHOUSE_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
    },
)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db)) -> Warehouse:
    warehouse = db.scalar(
        select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.deleted_at.is_(None))
    )
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found.")
    return warehouse


@router.put(
    "/{warehouse_id}",
    response_model=WarehouseRead,
    summary="Update warehouse",
    description="Updates warehouse code, name, or location.",
    response_description="Updated warehouse.",
    responses={
        200: {"content": {"application/json": {"example": examples.WAREHOUSE_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
        409: {"content": {"application/json": {"example": examples.CONFLICT_RESPONSE}}},
    },
)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    db: Session = Depends(get_db),
) -> Warehouse:
    warehouse = get_warehouse(warehouse_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(warehouse, field, value)
    db.commit()
    db.refresh(warehouse)
    return warehouse


@router.delete(
    "/{warehouse_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete warehouse",
    description="Marks a warehouse as deleted without removing the database record.",
    response_description="Warehouse deleted.",
    responses={404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}}},
)
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db)) -> None:
    warehouse = get_warehouse(warehouse_id, db)
    warehouse.deleted_at = datetime.now(UTC)
    db.commit()
