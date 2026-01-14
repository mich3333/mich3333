"""OrderShipped domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderShipped(DomainEvent):
    """Raised when an order is shipped"""

    event_type: ClassVar[str] = "order.shipped"

    order_id: UUID = field(kw_only=True)
    tracking_number: str = field(kw_only=True)
    shipping_address: str = field(kw_only=True)
