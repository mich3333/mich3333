"""OrderProcessingStarted domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class OrderProcessingStarted(DomainEvent):
    """Raised when order processing (fulfillment) begins"""

    event_type: ClassVar[str] = "order.processing_started"

    order_id: UUID = field(kw_only=True)
