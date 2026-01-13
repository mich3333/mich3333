"""LineItemRemoved domain event"""
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class LineItemRemoved(DomainEvent):
    """Raised when a line item is removed from an order"""

    event_type: ClassVar[str] = "order.line_item_removed"

    order_id: UUID
    line_item_id: UUID
