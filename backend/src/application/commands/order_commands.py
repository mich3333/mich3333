"""
Commands for Order operations.

Commands represent intent to change system state.
They are handled by Command Handlers.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from ...domain.order.value_objects.ids import (
    OrderId,
    CustomerId,
    ProductId,
    LineItemId,
    PaymentId
)
from ...domain.order.value_objects.address import Address


@dataclass(frozen=True)
class CreateOrderCommand:
    """Command to create a new order"""
    customer_id: CustomerId
    shipping_address: Address


@dataclass(frozen=True)
class AddLineItemCommand:
    """Command to add a line item to an order"""
    order_id: OrderId
    product_id: ProductId
    quantity: int
    unit_price: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class UpdateLineItemQuantityCommand:
    """Command to update line item quantity"""
    order_id: OrderId
    line_item_id: LineItemId
    new_quantity: int


@dataclass(frozen=True)
class RemoveLineItemCommand:
    """Command to remove a line item from an order"""
    order_id: OrderId
    line_item_id: LineItemId


@dataclass(frozen=True)
class SubmitOrderCommand:
    """Command to submit an order for payment"""
    order_id: OrderId


@dataclass(frozen=True)
class ConfirmPaymentCommand:
    """Command to confirm payment for an order"""
    order_id: OrderId
    payment_id: PaymentId
    amount_paid: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class ShipOrderCommand:
    """Command to ship an order"""
    order_id: OrderId
    tracking_number: str
    carrier: Optional[str] = None


@dataclass(frozen=True)
class DeliverOrderCommand:
    """Command to mark an order as delivered"""
    order_id: OrderId


@dataclass(frozen=True)
class CancelOrderCommand:
    """Command to cancel an order"""
    order_id: OrderId
    reason: Optional[str] = None
