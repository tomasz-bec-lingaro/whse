from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import DeliveryStatus


class DeliveryBase(BaseModel):
    supplier_id: int = Field(..., examples=[1])
    warehouse_id: int = Field(..., examples=[1])
    delivery_date: date = Field(..., examples=["2026-10-01"])
    status: DeliveryStatus = Field(default=DeliveryStatus.CREATED, examples=["CREATED"])


class DeliveryCreate(DeliveryBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "supplier_id": 1,
                    "warehouse_id": 1,
                    "delivery_date": "2026-10-01",
                    "status": "CREATED",
                }
            ]
        }
    )


class DeliveryUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "delivery_date": "2026-10-02",
                    "status": "RECEIVED",
                }
            ]
        }
    )

    supplier_id: int | None = Field(default=None, examples=[1])
    warehouse_id: int | None = Field(default=None, examples=[1])
    delivery_date: date | None = Field(default=None, examples=["2026-10-01"])
    status: DeliveryStatus | None = Field(default=None, examples=["RECEIVED"])


class DeliveryStatusUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "status": "RECEIVED",
                }
            ]
        }
    )

    status: DeliveryStatus = Field(..., examples=["RECEIVED"])


class DeliveryRead(DeliveryBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "supplier_id": 1,
                    "warehouse_id": 1,
                    "delivery_date": "2026-10-01",
                    "status": "CREATED",
                    "created_at": "2026-10-01T10:40:00Z",
                    "updated_at": None,
                }
            ]
        },
    )

    id: int
    created_at: datetime
    updated_at: datetime | None = None
