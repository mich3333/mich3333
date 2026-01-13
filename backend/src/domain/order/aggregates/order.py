"""
Order aggregate root.

The Order aggregate enforces all business rules and invariants related to orders.
It is the consistency boundary - all operations on an order go through this class.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ...shared.entity import AggregateRoot
from ..value_objects.ids import OrderId, CustomerId, ProductId, LineItemId, PaymentId
from ..value_objects.money import Money
from ..value_objects.address import Address, Quantity
from ..value_objects.order_status import OrderStatus
from ..exceptions import (
    InvalidStateTransitionError,
    OrderNotModifiableError,
    OrderNotCancellableError,
    EmptyOrderError,
    MinimumOrderValueError,
    InvalidQuantityError,
    ProductNotInOrderError,
)
from .line_item import LineItem


# Minimum order value (business rule)
MINIMUM_ORDER_VALUE = Money(Decimal("5.00"), "USD")


class Order(AggregateRoot):
    """
    Order aggregate root.

    Invariants:
    1. Order total must always equal sum of line item subtotals
    2. Cannot modify order after PENDING_PAYMENT status
    3. Cannot cancel order after PROCESSING status
    4. Cannot confirm payment unless in PENDING_PAYMENT status
    5. Minimum order value must be met to submit
    6. All line items must have positive quantity
    7. State transitions must follow valid paths

    State Machine:
    DRAFT → PENDING_PAYMENT → CONFIRMED → PROCESSING → SHIPPED → DELIVERED
      ↓
    CANCELLED
    """

    def __init__(
        self,
        id: OrderId,
        customer_id: CustomerId,
        status: OrderStatus,
        line_items: List[LineItem],
        shipping_address: Address,
        billing_address: Address,
        total: Money,
        created_at: datetime,
        updated_at: datetime,
        version: int = 0,
    ):
        super().__init__(id.value, version)
        self._order_id = id
        self._customer_id = customer_id
        self._status = status
        self._line_items = line_items
        self._shipping_address = shipping_address
        self._billing_address = billing_address
        self._total = total
        self._created_at = created_at
        self._updated_at = updated_at

        # Verify invariants on reconstitution
        self._verify_total_matches_line_items()

    @classmethod
    def create(
        cls,
        order_id: OrderId,
        customer_id: CustomerId,
        shipping_address: Address,
        billing_address: Address,
    ) -> "Order":
        """
        Factory method to create a new Order in DRAFT status.

        This is the only way to create a new Order.
        """
        from ..events.order_created import OrderCreated

        now = datetime.utcnow()
        order = cls(
            id=order_id,
            customer_id=customer_id,
            status=OrderStatus.DRAFT,
            line_items=[],
            shipping_address=shipping_address,
            billing_address=billing_address,
            total=Money.zero("USD"),
            created_at=now,
            updated_at=now,
            version=0,
        )

        order._raise_event(
            OrderCreated(
                order_id=order_id.value,
                customer_id=customer_id.value,
                occurred_at=now,
            )
        )

        return order

    # Properties (read-only access)

    @property
    def order_id(self) -> OrderId:
        return self._order_id

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def line_items(self) -> List[LineItem]:
        """Return copy to prevent external modification"""
        return self._line_items.copy()

    @property
    def shipping_address(self) -> Address:
        return self._shipping_address

    @property
    def billing_address(self) -> Address:
        return self._billing_address

    @property
    def total(self) -> Money:
        return self._total

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def item_count(self) -> int:
        """Total number of items in order"""
        return sum(item.quantity.value for item in self._line_items)

    # Domain operations

    def add_item(
        self,
        product_id: ProductId,
        product_name: str,
        quantity: Quantity,
        unit_price: Money,
    ) -> LineItemId:
        """
        Add a line item to the order.

        If product already exists, increase quantity.
        Otherwise, create new line item.

        Returns: ID of the line item (new or existing)

        Raises:
            OrderNotModifiableError: If order is past DRAFT status
            InvalidQuantityError: If quantity is invalid
        """
        from ..events.line_item_added import LineItemAdded

        if not self._status.is_modifiable():
            raise OrderNotModifiableError(
                f"Cannot add items to order in {self._status.value} status"
            )

        # Check if product already exists
        existing_item = self._find_line_item_by_product(product_id)

        if existing_item:
            # Update quantity of existing item
            existing_item.increase_quantity(quantity)
            line_item_id = existing_item.id
        else:
            # Create new line item
            line_item_id = LineItemId.generate()
            line_item = LineItem(
                id=line_item_id,
                product_id=product_id,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
            )
            self._line_items.append(line_item)

        self._recalculate_total()
        self._touch()

        self._raise_event(
            LineItemAdded(
                order_id=self._order_id.value,
                line_item_id=line_item_id.value,
                product_id=product_id.value,
                product_name=product_name,
                quantity=quantity.value,
                unit_price_amount=str(unit_price.amount),
                unit_price_currency=unit_price.currency,
                occurred_at=self._updated_at,
            )
        )

        return line_item_id

    def remove_item(self, line_item_id: LineItemId) -> None:
        """
        Remove a line item from the order.

        Raises:
            OrderNotModifiableError: If order is past DRAFT status
            ProductNotInOrderError: If line item not found
        """
        from ..events.line_item_removed import LineItemRemoved

        if not self._status.is_modifiable():
            raise OrderNotModifiableError(
                f"Cannot remove items from order in {self._status.value} status"
            )

        line_item = self._find_line_item_by_id(line_item_id)
        if not line_item:
            raise ProductNotInOrderError(f"Line item {line_item_id} not found in order")

        self._line_items.remove(line_item)
        self._recalculate_total()
        self._touch()

        self._raise_event(
            LineItemRemoved(
                order_id=self._order_id.value,
                line_item_id=line_item_id.value,
                occurred_at=self._updated_at,
            )
        )

    def update_item_quantity(self, line_item_id: LineItemId, new_quantity: Quantity) -> None:
        """
        Update quantity of a line item.

        Raises:
            OrderNotModifiableError: If order is past DRAFT status
            ProductNotInOrderError: If line item not found
        """
        from ..events.line_item_quantity_updated import LineItemQuantityUpdated

        if not self._status.is_modifiable():
            raise OrderNotModifiableError(
                f"Cannot update items in order in {self._status.value} status"
            )

        line_item = self._find_line_item_by_id(line_item_id)
        if not line_item:
            raise ProductNotInOrderError(f"Line item {line_item_id} not found in order")

        old_quantity = line_item.quantity
        line_item.update_quantity(new_quantity)

        self._recalculate_total()
        self._touch()

        self._raise_event(
            LineItemQuantityUpdated(
                order_id=self._order_id.value,
                line_item_id=line_item_id.value,
                old_quantity=old_quantity.value,
                new_quantity=new_quantity.value,
                occurred_at=self._updated_at,
            )
        )

    def submit(self) -> None:
        """
        Submit the order for payment.

        Transitions: DRAFT → PENDING_PAYMENT

        Raises:
            InvalidStateTransitionError: If not in DRAFT status
            EmptyOrderError: If no line items
            MinimumOrderValueError: If total below minimum
        """
        from ..events.order_submitted import OrderSubmitted

        self._ensure_valid_transition(OrderStatus.PENDING_PAYMENT)

        if not self._line_items:
            raise EmptyOrderError("Cannot submit order with no line items")

        if self._total < MINIMUM_ORDER_VALUE:
            raise MinimumOrderValueError(
                f"Order total {self._total} is below minimum {MINIMUM_ORDER_VALUE}"
            )

        self._status = OrderStatus.PENDING_PAYMENT
        self._touch()

        self._raise_event(
            OrderSubmitted(
                order_id=self._order_id.value,
                customer_id=self._customer_id.value,
                total_amount=str(self._total.amount),
                total_currency=self._total.currency,
                item_count=self.item_count,
                occurred_at=self._updated_at,
            )
        )

    def confirm_payment(self, payment_id: PaymentId) -> None:
        """
        Confirm payment for the order.

        Transitions: PENDING_PAYMENT → CONFIRMED

        Raises:
            InvalidStateTransitionError: If not in PENDING_PAYMENT status
        """
        from ..events.payment_confirmed import PaymentConfirmed

        self._ensure_valid_transition(OrderStatus.CONFIRMED)

        self._status = OrderStatus.CONFIRMED
        self._touch()

        self._raise_event(
            PaymentConfirmed(
                order_id=self._order_id.value,
                payment_id=payment_id.value,
                amount=str(self._total.amount),
                currency=self._total.currency,
                occurred_at=self._updated_at,
            )
        )

    def start_processing(self) -> None:
        """
        Start processing the order (fulfillment begins).

        Transitions: CONFIRMED → PROCESSING

        Raises:
            InvalidStateTransitionError: If not in CONFIRMED status
        """
        from ..events.order_processing_started import OrderProcessingStarted

        self._ensure_valid_transition(OrderStatus.PROCESSING)

        self._status = OrderStatus.PROCESSING
        self._touch()

        self._raise_event(
            OrderProcessingStarted(
                order_id=self._order_id.value,
                occurred_at=self._updated_at,
            )
        )

    def ship(self, tracking_number: str) -> None:
        """
        Mark order as shipped.

        Transitions: PROCESSING → SHIPPED

        Raises:
            InvalidStateTransitionError: If not in PROCESSING status
        """
        from ..events.order_shipped import OrderShipped

        self._ensure_valid_transition(OrderStatus.SHIPPED)

        if not tracking_number or not tracking_number.strip():
            raise ValueError("Tracking number is required")

        self._status = OrderStatus.SHIPPED
        self._touch()

        self._raise_event(
            OrderShipped(
                order_id=self._order_id.value,
                tracking_number=tracking_number,
                shipping_address=str(self._shipping_address),
                occurred_at=self._updated_at,
            )
        )

    def deliver(self) -> None:
        """
        Mark order as delivered.

        Transitions: SHIPPED → DELIVERED

        Raises:
            InvalidStateTransitionError: If not in SHIPPED status
        """
        from ..events.order_delivered import OrderDelivered

        self._ensure_valid_transition(OrderStatus.DELIVERED)

        self._status = OrderStatus.DELIVERED
        self._touch()

        self._raise_event(
            OrderDelivered(
                order_id=self._order_id.value,
                occurred_at=self._updated_at,
            )
        )

    def cancel(self, reason: str) -> None:
        """
        Cancel the order.

        Valid from: DRAFT, PENDING_PAYMENT
        Transitions to: CANCELLED

        Raises:
            OrderNotCancellableError: If order cannot be cancelled
        """
        from ..events.order_cancelled import OrderCancelled

        if not self._status.is_cancellable():
            raise OrderNotCancellableError(
                f"Cannot cancel order in {self._status.value} status"
            )

        if not reason or not reason.strip():
            raise ValueError("Cancellation reason is required")

        self._status = OrderStatus.CANCELLED
        self._touch()

        self._raise_event(
            OrderCancelled(
                order_id=self._order_id.value,
                reason=reason,
                occurred_at=self._updated_at,
            )
        )

    # Private helper methods

    def _find_line_item_by_product(self, product_id: ProductId) -> Optional[LineItem]:
        """Find line item by product ID"""
        for item in self._line_items:
            if item.product_id == product_id:
                return item
        return None

    def _find_line_item_by_id(self, line_item_id: LineItemId) -> Optional[LineItem]:
        """Find line item by its ID"""
        for item in self._line_items:
            if item.id == line_item_id:
                return item
        return None

    def _recalculate_total(self) -> None:
        """
        Recalculate order total from line items.

        Maintains invariant: total = sum(line_item.subtotal())
        """
        if not self._line_items:
            self._total = Money.zero("USD")
        else:
            self._total = sum(
                (item.subtotal() for item in self._line_items),
                start=Money.zero("USD"),
            )

    def _verify_total_matches_line_items(self) -> None:
        """
        Verify that stored total matches calculated total.

        Called on reconstitution to ensure data integrity.
        """
        calculated_total = sum(
            (item.subtotal() for item in self._line_items),
            start=Money.zero("USD"),
        )

        if self._total != calculated_total:
            raise ValueError(
                f"Order total {self._total} does not match "
                f"calculated total {calculated_total}"
            )

    def _ensure_valid_transition(self, target_status: OrderStatus) -> None:
        """
        Ensure state transition is valid.

        Raises:
            InvalidStateTransitionError: If transition is invalid
        """
        if not self._status.can_transition_to(target_status):
            raise InvalidStateTransitionError(
                f"Cannot transition from {self._status.value} to {target_status.value}"
            )

    def _touch(self) -> None:
        """Update the updated_at timestamp"""
        self._updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"Order(id={self._order_id}, customer_id={self._customer_id}, "
            f"status={self._status.value}, total={self._total}, "
            f"items={len(self._line_items)})"
        )
