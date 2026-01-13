"""
OrderStatus value object.

Represents the state of an order in its lifecycle.
Defines valid state transitions.
"""
from enum import Enum
from typing import Set


class OrderStatus(str, Enum):
    """
    Order status enumeration.

    State machine:
    DRAFT → PENDING_PAYMENT → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
      ↓
    CANCELLED
    """
    DRAFT = "draft"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    def can_transition_to(self, target: "OrderStatus") -> bool:
        """Check if transition to target status is valid"""
        valid_transitions = self._get_valid_transitions()
        return target in valid_transitions

    def _get_valid_transitions(self) -> Set["OrderStatus"]:
        """Get set of valid next states"""
        transitions = {
            OrderStatus.DRAFT: {
                OrderStatus.PENDING_PAYMENT,
                OrderStatus.CANCELLED,
            },
            OrderStatus.PENDING_PAYMENT: {
                OrderStatus.CONFIRMED,
                OrderStatus.CANCELLED,
            },
            OrderStatus.CONFIRMED: {
                OrderStatus.PROCESSING,
            },
            OrderStatus.PROCESSING: {
                OrderStatus.SHIPPED,
            },
            OrderStatus.SHIPPED: {
                OrderStatus.DELIVERED,
            },
            OrderStatus.DELIVERED: set(),  # Terminal state
            OrderStatus.CANCELLED: set(),  # Terminal state
        }
        return transitions[self]

    def is_modifiable(self) -> bool:
        """Check if order can be modified in this state"""
        return self == OrderStatus.DRAFT

    def is_cancellable(self) -> bool:
        """Check if order can be cancelled in this state"""
        return self in {OrderStatus.DRAFT, OrderStatus.PENDING_PAYMENT}

    def is_terminal(self) -> bool:
        """Check if this is a terminal state"""
        return self in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}

    def is_paid(self) -> bool:
        """Check if payment has been confirmed"""
        return self in {
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
        }
