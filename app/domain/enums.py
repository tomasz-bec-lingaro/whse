from enum import StrEnum


class DeliveryStatus(StrEnum):
    CREATED = "CREATED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"
