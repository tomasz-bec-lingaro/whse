from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DeliveryDocumentRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "delivery_id": 1,
                    "filename": "delivery-note.pdf",
                    "content_type": "application/pdf",
                    "size_bytes": 24576,
                    "uploaded_at": "2026-10-01T10:45:00Z",
                }
            ]
        },
    )

    id: int
    delivery_id: int
    filename: str = Field(..., examples=["delivery-note.pdf"])
    content_type: str = Field(..., examples=["application/pdf"])
    size_bytes: int
    uploaded_at: datetime
