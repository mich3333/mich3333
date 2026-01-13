"""OrderSubmitted domain event"""
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    """Raised when an order is submitted for payment"""

    event_type: ClassVar[str] = "order.submitted"

    order_id: UUID
    customer_id: UUID
    total_amount: str
    total_currency: str
    item_count: int
