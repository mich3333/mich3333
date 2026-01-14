"""LineItemQuantityUpdated domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class LineItemQuantityUpdated(DomainEvent):
    """Raised when a line item quantity is updated"""

    event_type: ClassVar[str] = "order.line_item_quantity_updated"

    order_id: UUID = field(kw_only=True)
    line_item_id: UUID = field(kw_only=True)
    old_quantity: int = field(kw_only=True)
    new_quantity: int = field(kw_only=True)
