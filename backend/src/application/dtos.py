"""
Data Transfer Objects (DTOs) for Application Layer.

DTOs are used to transfer data between layers and across boundaries.
They are simple data structures without business logic.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID


# ========== Request DTOs ==========

@dataclass
class CreateOrderDTO:
    """DTO for creating a new order"""
    customer_id: str  # UUID as string
    shipping_address: "AddressDTO"


@dataclass
class AddressDTO:
    """DTO for address value object"""
    street: str
    city: str
    state: str
    postal_code: str
    country: str


@dataclass
class AddLineItemDTO:
    """DTO for adding a line item to an order"""
    order_id: str  # UUID as string
    product_id: str  # UUID as string
    quantity: int
    unit_price: Decimal
    currency: str = "USD"


@dataclass
class UpdateLineItemQuantityDTO:
    """DTO for updating line item quantity"""
    order_id: str
    line_item_id: str
    new_quantity: int


@dataclass
class RemoveLineItemDTO:
    """DTO for removing a line item"""
    order_id: str
    line_item_id: str


@dataclass
class SubmitOrderDTO:
    """DTO for submitting an order"""
    order_id: str


@dataclass
class ConfirmPaymentDTO:
    """DTO for confirming payment"""
    order_id: str
    payment_id: str
    amount_paid: Decimal
    currency: str = "USD"


@dataclass
class ShipOrderDTO:
    """DTO for shipping an order"""
    order_id: str
    tracking_number: str
    carrier: Optional[str] = None


@dataclass
class DeliverOrderDTO:
    """DTO for marking order as delivered"""
    order_id: str


@dataclass
class CancelOrderDTO:
    """DTO for cancelling an order"""
    order_id: str
    reason: Optional[str] = None


# ========== Response DTOs ==========

@dataclass
class OrderResponseDTO:
    """DTO for order response"""
    id: str
    customer_id: str
    status: str
    total: Decimal
    currency: str
    line_items: List["LineItemResponseDTO"]
    shipping_address: AddressDTO
    created_at: datetime
    submitted_at: Optional[datetime] = None
    payment_confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    tracking_number: Optional[str] = None
    version: int = 0


@dataclass
class LineItemResponseDTO:
    """DTO for line item response"""
    id: str
    product_id: str
    quantity: int
    unit_price: Decimal
    currency: str
    subtotal: Decimal


@dataclass
class ErrorResponseDTO:
    """DTO for error responses"""
    error_type: str
    message: str
    details: Optional[dict] = None
