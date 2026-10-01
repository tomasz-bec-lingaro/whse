from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WarehouseBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=64, examples=["WAW-01"])
    name: str = Field(..., min_length=1, max_length=255, examples=["Warsaw Main Warehouse"])
    location: str | None = Field(default=None, max_length=255, examples=["Warsaw"])


class WarehouseCreate(WarehouseBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "code": "WAW-01",
                    "name": "Warsaw Main Warehouse",
                    "location": "Warsaw",
                }
            ]
        }
    )


class WarehouseUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Warsaw Central Warehouse",
                    "location": "Warsaw, ul. Magazynowa 1",
                }
            ]
        }
    )

    code: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)


class WarehouseRead(WarehouseBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "code": "WAW-01",
                    "name": "Warsaw Main Warehouse",
                    "location": "Warsaw",
                    "created_at": "2026-10-01T10:35:00Z",
                    "updated_at": None,
                }
            ]
        },
    )

    id: int
    created_at: datetime
    updated_at: datetime | None = None
