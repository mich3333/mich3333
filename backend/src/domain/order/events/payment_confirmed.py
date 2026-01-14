"""PaymentConfirmed domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class PaymentConfirmed(DomainEvent):
    """Raised when payment for an order is confirmed"""

    event_type: ClassVar[str] = "order.payment_confirmed"

    order_id: UUID = field(kw_only=True)
    payment_id: UUID = field(kw_only=True)
    amount: str = field(kw_only=True)
    currency: str = field(kw_only=True)
