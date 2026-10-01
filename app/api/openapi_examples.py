SUPPLIER_RESPONSE = {
    "id": 1,
    "name": "ACME Logistics",
    "tax_id": "PL1234567890",
    "email": "ops@acme.example",
    "phone": "+48123456789",
    "created_at": "2026-10-01T10:30:00Z",
    "updated_at": None,
}

SUPPLIERS_PAGE_RESPONSE = {
    "items": [SUPPLIER_RESPONSE],
    "page": 1,
    "size": 20,
    "total": 1,
}

WAREHOUSE_RESPONSE = {
    "id": 1,
    "code": "WAW-01",
    "name": "Warsaw Main Warehouse",
    "location": "Warsaw",
    "created_at": "2026-10-01T10:35:00Z",
    "updated_at": None,
}

WAREHOUSES_PAGE_RESPONSE = {
    "items": [WAREHOUSE_RESPONSE],
    "page": 1,
    "size": 20,
    "total": 1,
}

DELIVERY_RESPONSE = {
    "id": 1,
    "supplier_id": 1,
    "warehouse_id": 1,
    "delivery_date": "2026-10-01",
    "status": "CREATED",
    "created_at": "2026-10-01T10:40:00Z",
    "updated_at": None,
}

DELIVERIES_PAGE_RESPONSE = {
    "items": [DELIVERY_RESPONSE],
    "page": 1,
    "size": 20,
    "total": 1,
}

DELIVERY_DOCUMENT_RESPONSE = {
    "id": 1,
    "delivery_id": 1,
    "filename": "delivery-note.pdf",
    "content_type": "application/pdf",
    "blob_path": "deliveries/1/documents/1/delivery-note.pdf",
    "size_bytes": 24576,
    "uploaded_at": "2026-10-01T10:45:00Z",
}

DELIVERY_DOCUMENTS_RESPONSE = [DELIVERY_DOCUMENT_RESPONSE]

NOT_FOUND_RESPONSE = {"detail": "Resource not found."}
CONFLICT_RESPONSE = {"detail": "The submitted data conflicts with existing records."}
INVALID_TRANSITION_RESPONSE = {"detail": "Delivery status transition is not allowed."}
INVALID_FILE_RESPONSE = {"detail": "Only PDF and JPG files are supported."}
