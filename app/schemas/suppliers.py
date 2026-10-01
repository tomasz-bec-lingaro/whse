from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, examples=["ACME Logistics"])
    tax_id: str | None = Field(default=None, max_length=64, examples=["PL1234567890"])
    email: str | None = Field(default=None, max_length=255, examples=["ops@example.com"])
    phone: str | None = Field(default=None, max_length=64, examples=["+48123456789"])


class SupplierCreate(SupplierBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "ACME Logistics",
                    "tax_id": "PL1234567890",
                    "email": "ops@acme.example",
                    "phone": "+48123456789",
                }
            ]
        }
    )


class SupplierUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "ACME Logistics Sp. z o.o.",
                    "email": "warehouse@acme.example",
                    "phone": "+48987654321",
                }
            ]
        }
    )

    name: str | None = Field(default=None, min_length=1, max_length=255)
    tax_id: str | None = Field(default=None, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=64)


class SupplierRead(SupplierBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "ACME Logistics",
                    "tax_id": "PL1234567890",
                    "email": "ops@acme.example",
                    "phone": "+48123456789",
                    "created_at": "2026-10-01T10:30:00Z",
                    "updated_at": None,
                }
            ]
        },
    )

    id: int
    created_at: datetime
    updated_at: datetime | None = None
