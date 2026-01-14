"""OrderSubmitted domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    """Raised when an order is submitted for payment"""

    event_type: ClassVar[str] = "order.submitted"

    order_id: UUID = field(kw_only=True)
    customer_id: UUID = field(kw_only=True)
    total_amount: str = field(kw_only=True)
    total_currency: str = field(kw_only=True)
    item_count: int = field(kw_only=True)
