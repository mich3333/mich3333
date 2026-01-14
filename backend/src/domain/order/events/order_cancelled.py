"""OrderCancelled domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderCancelled(DomainEvent):
    """Raised when an order is cancelled"""

    event_type: ClassVar[str] = "order.cancelled"

    order_id: UUID = field(kw_only=True)
    reason: str = field(kw_only=True)
