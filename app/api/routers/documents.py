from datetime import UTC, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api import openapi_examples as examples
from app.api.dependencies import enforce_upload_rate_limit, get_storage
from app.core.config import settings
from app.core.errors import StorageOperationError
from app.db.models import Delivery, DeliveryDocument
from app.db.session import get_db
from app.schemas.documents import DeliveryDocumentRead
from app.services.documents import build_document_blob_path, sanitize_filename, validate_upload
from app.storage.base import BlobStorage

router = APIRouter()


def _get_delivery_or_404(delivery_id: int, db: Session) -> Delivery:
    delivery = db.scalar(
        select(Delivery).where(Delivery.id == delivery_id, Delivery.deleted_at.is_(None))
    )
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found.")
    return delivery


def _get_document_or_404(delivery_id: int, document_id: int, db: Session) -> DeliveryDocument:
    document = db.scalar(
        select(DeliveryDocument)
        .join(Delivery, Delivery.id == DeliveryDocument.delivery_id)
        .where(
            DeliveryDocument.id == document_id,
            DeliveryDocument.delivery_id == delivery_id,
            DeliveryDocument.deleted_at.is_(None),
            Delivery.deleted_at.is_(None),
        )
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Delivery document not found.")
    return document


@router.post(
    "/{delivery_id}/documents",
    response_model=DeliveryDocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Upload delivery document",
    description=(
        "Uploads a PDF or JPG delivery document to Blob Storage and stores document "
        "metadata in the database."
    ),
    response_description="Uploaded document metadata.",
    responses={
        201: {"content": {"application/json": {"example": examples.DELIVERY_DOCUMENT_RESPONSE}}},
        400: {"content": {"application/json": {"example": examples.INVALID_FILE_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
    },
)
def upload_document(
    delivery_id: int,
    _rate_limit: None = Depends(enforce_upload_rate_limit),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage: BlobStorage = Depends(get_storage),
) -> DeliveryDocument:
    _get_delivery_or_404(delivery_id, db)

    file.file.seek(0)
    content = file.file.read()
    validate_upload(
        filename=file.filename,
        content_type=file.content_type,
        content=content,
        size_bytes=len(content),
        max_size_mb=settings.max_upload_size_mb,
    )

    document = DeliveryDocument(
        delivery_id=delivery_id,
        filename=sanitize_filename(file.filename or "document"),
        content_type=file.content_type or "application/octet-stream",
        blob_path="pending",
        size_bytes=len(content),
    )
    db.add(document)
    db.flush()

    document.blob_path = build_document_blob_path(
        delivery_id=delivery_id,
        document_id=document.id,
        filename=document.filename,
    )

    storage.upload(
        path=document.blob_path,
        data=content,
        content_type=document.content_type,
    )
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        try:
            storage.delete(document.blob_path)
        except StorageOperationError:
            pass
        raise
    db.refresh(document)
    return document


@router.get(
    "/{delivery_id}/documents",
    response_model=list[DeliveryDocumentRead],
    summary="List delivery documents",
    description="Returns active document metadata records for a delivery.",
    response_description="Delivery documents list.",
    responses={
        200: {"content": {"application/json": {"example": examples.DELIVERY_DOCUMENTS_RESPONSE}}},
        404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}},
    },
)
def list_documents(delivery_id: int, db: Session = Depends(get_db)) -> list[DeliveryDocument]:
    _get_delivery_or_404(delivery_id, db)
    return list(
        db.scalars(
            select(DeliveryDocument)
            .where(
                DeliveryDocument.delivery_id == delivery_id,
                DeliveryDocument.deleted_at.is_(None),
            )
            .order_by(DeliveryDocument.uploaded_at.desc(), DeliveryDocument.id.desc())
        ).all()
    )


@router.get(
    "/{delivery_id}/documents/{document_id}/download",
    summary="Download delivery document",
    description="Streams the requested delivery document from Blob Storage through the API.",
    response_description="Binary file stream.",
    responses={404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}}},
)
def download_document(
    delivery_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    storage: BlobStorage = Depends(get_storage),
) -> StreamingResponse:
    document = _get_document_or_404(delivery_id, document_id, db)
    return StreamingResponse(
        storage.download_chunks(document.blob_path),
        media_type=document.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{document.filename}"',
            "Content-Length": str(document.size_bytes),
        },
    )


@router.delete(
    "/{delivery_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete delivery document",
    description="Marks document metadata as deleted and leaves the blob object in storage.",
    response_description="Document deleted.",
    responses={404: {"content": {"application/json": {"example": examples.NOT_FOUND_RESPONSE}}}},
)
def delete_document(
    delivery_id: int,
    document_id: int,
    db: Session = Depends(get_db),
) -> None:
    document = _get_document_or_404(delivery_id, document_id, db)
    document.deleted_at = datetime.now(UTC)
    db.commit()
