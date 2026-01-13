"""OrderShipped domain event"""
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    """Raised when an order is shipped"""

    event_type: ClassVar[str] = "order.shipped"

    order_id: UUID
    tracking_number: str
    shipping_address: str
