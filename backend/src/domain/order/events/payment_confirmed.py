"""PaymentConfirmed domain event"""
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class PaymentConfirmed(DomainEvent):
    """Raised when payment for an order is confirmed"""

    event_type: ClassVar[str] = "order.payment_confirmed"

    order_id: UUID
    payment_id: UUID
    amount: str
    currency: str
