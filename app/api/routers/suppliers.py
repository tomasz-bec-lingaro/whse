from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api import openapi_examples as examples
from app.db.models import Supplier
from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.suppliers import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter()


@router.post(
    "",
    response_model=SupplierRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create supplier",
    description="Creates a supplier that can be assigned to warehouse deliveries.",
    response_description="Created supplier.",
    responses={
        201: {"content": {"application/json": {"example": examples.SUPPLIER_RESPONSE}}},
        409: {"content": {"application/json": {"example": examples.CONFLICT_RESPONSE}}},
    },
)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)) -> Supplier:
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get(
    "",
    response_model=PaginatedResponse[SupplierRead],
    summary="List suppliers",
    description="Returns active suppliers with page-based pagination.",
    response_description="Paginated suppliers list.",
    responses={
        200: {"content": {"application/json": {"example": examples.SUPPLIERS_PAGE_RESPONSE}}}
    },
)
def list_suppliers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedResponse[SupplierRead]:
    filters = Supplier.deleted_at.is_(None)
    total = db.scalar(select(func.count()).select_from(Supplier).where(filters)) or 0
    items = db.scalars(
        select(Supplier).where(filters).order_by(Supplier.id).offset((page - 1) * size).limit(size)
    ).all()
    return PaginatedResponse[SupplierRead](items=items, page=page, size=size, total=total)


@router.get(
    "/{supplier_id}",
    response_model=SupplierRead,
    summary="Get supplier",
    description="Returns a single active supplier by ID.",
    response_description="Supplier details.",
    responses={
        200: {"content": {"application/json": {"example": examples.SUPPLIER_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
    },
)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)) -> Supplier:
    supplier = db.scalar(
        select(Supplier).where(Supplier.id == supplier_id, Supplier.deleted_at.is_(None))
    )
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found.")
    return supplier


@router.put(
    "/{supplier_id}",
    response_model=SupplierRead,
    summary="Update supplier",
    description="Updates supplier contact or identification data.",
    response_description="Updated supplier.",
    responses={
        200: {"content": {"application/json": {"example": examples.SUPPLIER_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
        409: {"content": {"application/json": {"example": examples.CONFLICT_RESPONSE}}},
    },
)
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
) -> Supplier:
    supplier = get_supplier(supplier_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete supplier",
    description="Marks a supplier as deleted without removing the database record.",
    response_description="Supplier deleted.",
    responses={404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}}},
)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)) -> None:
    supplier = get_supplier(supplier_id, db)
    supplier.deleted_at = datetime.now(UTC)
    db.commit()
