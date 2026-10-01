from app.domain.enums import DeliveryStatus

ALLOWED_TRANSITIONS: dict[DeliveryStatus, set[DeliveryStatus]] = {
    DeliveryStatus.CREATED: {DeliveryStatus.RECEIVED, DeliveryStatus.CANCELLED},
    DeliveryStatus.RECEIVED: set(),
    DeliveryStatus.CANCELLED: set(),
}


def is_transition_allowed(current: DeliveryStatus, target: DeliveryStatus) -> bool:
    if current == target:
        return True
    return target in ALLOWED_TRANSITIONS[current]
