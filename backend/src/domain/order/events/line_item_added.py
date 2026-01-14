"""LineItemAdded domain event"""
from dataclasses import dataclass, field
from typing import ClassVar
from uuid import UUID

from ...shared.domain_event import DomainEvent


@dataclass(frozen=True)
class LineItemAdded(DomainEvent):
    """Raised when a line item is added to an order"""

    event_type: ClassVar[str] = "order.line_item_added"

    order_id: UUID = field(kw_only=True)
    line_item_id: UUID = field(kw_only=True)
    product_id: UUID = field(kw_only=True)
    product_name: str = field(kw_only=True)
    quantity: int = field(kw_only=True)
    unit_price_amount: str = field(kw_only=True)
    unit_price_currency: str = field(kw_only=True)
