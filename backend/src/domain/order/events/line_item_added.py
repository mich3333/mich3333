"""LineItemAdded domain event"""
from dataclasses import dataclass
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class LineItemAdded(DomainEvent):
    """Raised when a line item is added to an order"""

    event_type: ClassVar[str] = "order.line_item_added"

    order_id: UUID
    line_item_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price_amount: str
    unit_price_currency: str
