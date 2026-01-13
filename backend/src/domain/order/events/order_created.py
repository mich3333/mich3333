"""OrderCreated domain event"""
from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderCreated(DomainEvent):
    """Raised when a new order is created"""

    event_type: ClassVar[str] = "order.created"

    order_id: UUID
    customer_id: UUID
