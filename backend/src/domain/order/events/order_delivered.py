"""OrderDelivered domain event"""
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderDelivered(DomainEvent):
    """Raised when an order is delivered"""

    event_type: ClassVar[str] = "order.delivered"

    order_id: UUID
