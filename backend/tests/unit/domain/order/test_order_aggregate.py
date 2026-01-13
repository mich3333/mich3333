"""
Unit tests for Order aggregate root.

Tests demonstrate:
- State machine transitions
- Business invariants
- Domain events
- Error conditions
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.domain.order.aggregates.order import Order, MINIMUM_ORDER_VALUE
from src.domain.order.value_objects.ids import OrderId, CustomerId, ProductId, LineItemId, PaymentId
from src.domain.order.value_objects.money import Money
from src.domain.order.value_objects.address import Address, Quantity
from src.domain.order.value_objects.order_status import OrderStatus
from src.domain.order.exceptions import (
    InvalidStateTransitionError,
    OrderNotModifiableError,
    OrderNotCancellableError,
    EmptyOrderError,
    MinimumOrderValueError,
    ProductNotInOrderError,
)
from src.domain.order.events.order_created import OrderCreated
from src.domain.order.events.line_item_added import LineItemAdded
from src.domain.order.events.order_submitted import OrderSubmitted
from src.domain.order.events.payment_confirmed import PaymentConfirmed
from src.domain.order.events.order_cancelled import OrderCancelled


@pytest.fixture
def shipping_address():
    return Address(
        street="123 Main St",
        city="San Francisco",
        state="CA",
        postal_code="94102",
        country="USA"
    )


@pytest.fixture
def billing_address():
    return Address(
        street="456 Market St",
        city="San Francisco",
        state="CA",
        postal_code="94103",
        country="USA"
    )


@pytest.fixture
def order_id():
    return OrderId.generate()


@pytest.fixture
def customer_id():
    return CustomerId.generate()


@pytest.fixture
def product_id():
    return ProductId.generate()


@pytest.fixture
def draft_order(order_id, customer_id, shipping_address, billing_address):
    """Create a fresh order in DRAFT status"""
    return Order.create(
        order_id=order_id,
        customer_id=customer_id,
        shipping_address=shipping_address,
        billing_address=billing_address,
    )


class TestOrderCreation:
    """Test Order factory method"""

    def test_create_order_in_draft_status(self, order_id, customer_id, shipping_address, billing_address):
        order = Order.create(
            order_id=order_id,
            customer_id=customer_id,
            shipping_address=shipping_address,
            billing_address=billing_address,
        )

        assert order.order_id == order_id
        assert order.customer_id == customer_id
        assert order.status == OrderStatus.DRAFT
        assert len(order.line_items) == 0
        assert order.total.is_zero()
        assert order.version == 0

    def test_create_order_raises_order_created_event(self, order_id, customer_id, shipping_address, billing_address):
        order = Order.create(
            order_id=order_id,
            customer_id=customer_id,
            shipping_address=shipping_address,
            billing_address=billing_address,
        )

        events = order.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], OrderCreated)
        assert events[0].order_id == order_id.value
        assert events[0].customer_id == customer_id.value


class TestAddingLineItems:
    """Test adding line items to order"""

    def test_add_item_to_draft_order(self, draft_order, product_id):
        line_item_id = draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(2),
            unit_price=Money.from_string("19.99", "USD"),
        )

        assert line_item_id is not None
        assert len(draft_order.line_items) == 1
        assert draft_order.total == Money.from_string("39.98", "USD")
        assert draft_order.item_count == 2

    def test_add_same_product_increases_quantity(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(2),
            unit_price=Money.from_string("10.00", "USD"),
        )

        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(3),
            unit_price=Money.from_string("10.00", "USD"),
        )

        assert len(draft_order.line_items) == 1  # Still one line item
        assert draft_order.line_items[0].quantity.value == 5  # 2 + 3
        assert draft_order.total == Money.from_string("50.00", "USD")

    def test_add_different_products_creates_multiple_line_items(self, draft_order):
        product1 = ProductId.generate()
        product2 = ProductId.generate()

        draft_order.add_item(
            product_id=product1,
            product_name="Product 1",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )

        draft_order.add_item(
            product_id=product2,
            product_name="Product 2",
            quantity=Quantity(2),
            unit_price=Money.from_string("20.00", "USD"),
        )

        assert len(draft_order.line_items) == 2
        assert draft_order.total == Money.from_string("50.00", "USD")

    def test_add_item_raises_event(self, draft_order, product_id):
        draft_order.collect_events()  # Clear creation event

        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(2),
            unit_price=Money.from_string("19.99", "USD"),
        )

        events = draft_order.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], LineItemAdded)
        assert events[0].product_id == product_id.value
        assert events[0].quantity == 2

    def test_cannot_add_item_to_submitted_order(self, draft_order, product_id):
        # Add item and submit
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(2),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()

        # Try to add another item
        with pytest.raises(OrderNotModifiableError, match="Cannot add items"):
            draft_order.add_item(
                product_id=ProductId.generate(),
                product_name="Another Product",
                quantity=Quantity(1),
                unit_price=Money.from_string("5.00", "USD"),
            )


class TestRemovingLineItems:
    """Test removing line items from order"""

    def test_remove_item_from_draft_order(self, draft_order, product_id):
        line_item_id = draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(2),
            unit_price=Money.from_string("10.00", "USD"),
        )

        draft_order.remove_item(line_item_id)

        assert len(draft_order.line_items) == 0
        assert draft_order.total.is_zero()

    def test_remove_nonexistent_item_raises_error(self, draft_order):
        with pytest.raises(ProductNotInOrderError):
            draft_order.remove_item(LineItemId.generate())

    def test_cannot_remove_item_from_submitted_order(self, draft_order, product_id):
        line_item_id = draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(2),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()

        with pytest.raises(OrderNotModifiableError):
            draft_order.remove_item(line_item_id)


class TestOrderSubmission:
    """Test submitting order for payment"""

    def test_submit_order_with_sufficient_value(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )

        draft_order.submit()

        assert draft_order.status == OrderStatus.PENDING_PAYMENT

    def test_submit_raises_event(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.collect_events()  # Clear previous events

        draft_order.submit()

        events = draft_order.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], OrderSubmitted)
        assert events[0].order_id == draft_order.order_id.value

    def test_cannot_submit_empty_order(self, draft_order):
        with pytest.raises(EmptyOrderError, match="no line items"):
            draft_order.submit()

    def test_cannot_submit_order_below_minimum_value(self, draft_order, product_id):
        # Add item below minimum ($5)
        draft_order.add_item(
            product_id=product_id,
            product_name="Cheap Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("3.00", "USD"),
        )

        with pytest.raises(MinimumOrderValueError, match="below minimum"):
            draft_order.submit()

    def test_can_only_submit_from_draft_status(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()

        # Try to submit again
        with pytest.raises(InvalidStateTransitionError):
            draft_order.submit()


class TestPaymentConfirmation:
    """Test payment confirmation"""

    def test_confirm_payment_transitions_to_confirmed(self, draft_order, product_id):
        # Setup: submit order
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()

        # Confirm payment
        payment_id = PaymentId.generate()
        draft_order.confirm_payment(payment_id)

        assert draft_order.status == OrderStatus.CONFIRMED

    def test_confirm_payment_raises_event(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()
        draft_order.collect_events()  # Clear previous events

        payment_id = PaymentId.generate()
        draft_order.confirm_payment(payment_id)

        events = draft_order.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], PaymentConfirmed)
        assert events[0].payment_id == payment_id.value

    def test_can_only_confirm_payment_from_pending_payment(self, draft_order):
        payment_id = PaymentId.generate()

        with pytest.raises(InvalidStateTransitionError):
            draft_order.confirm_payment(payment_id)


class TestOrderCancellation:
    """Test order cancellation"""

    def test_cancel_draft_order(self, draft_order):
        draft_order.cancel("Customer requested")
        assert draft_order.status == OrderStatus.CANCELLED

    def test_cancel_pending_payment_order(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()

        draft_order.cancel("Customer changed mind")
        assert draft_order.status == OrderStatus.CANCELLED

    def test_cancel_raises_event(self, draft_order):
        draft_order.collect_events()  # Clear creation event

        draft_order.cancel("Test reason")

        events = draft_order.collect_events()
        assert len(events) == 1
        assert isinstance(events[0], OrderCancelled)
        assert events[0].reason == "Test reason"

    def test_cannot_cancel_confirmed_order(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()
        draft_order.confirm_payment(PaymentId.generate())

        with pytest.raises(OrderNotCancellableError):
            draft_order.cancel("Too late")

    def test_cancel_requires_reason(self, draft_order):
        with pytest.raises(ValueError, match="reason is required"):
            draft_order.cancel("")


class TestStateMachine:
    """Test complete state machine transitions"""

    def test_happy_path_full_lifecycle(self, draft_order, product_id):
        # Start in DRAFT
        assert draft_order.status == OrderStatus.DRAFT

        # Add items
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )

        # Submit → PENDING_PAYMENT
        draft_order.submit()
        assert draft_order.status == OrderStatus.PENDING_PAYMENT

        # Confirm payment → CONFIRMED
        draft_order.confirm_payment(PaymentId.generate())
        assert draft_order.status == OrderStatus.CONFIRMED

        # Start processing → PROCESSING
        draft_order.start_processing()
        assert draft_order.status == OrderStatus.PROCESSING

        # Ship → SHIPPED
        draft_order.ship("TRACK123")
        assert draft_order.status == OrderStatus.SHIPPED

        # Deliver → DELIVERED
        draft_order.deliver()
        assert draft_order.status == OrderStatus.DELIVERED

    def test_cancellation_path(self, draft_order, product_id):
        # Add items and submit
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )
        draft_order.submit()

        # Cancel before payment
        draft_order.cancel("Customer cancelled")
        assert draft_order.status == OrderStatus.CANCELLED


class TestInvariants:
    """Test business invariants are maintained"""

    def test_total_always_matches_line_items(self, draft_order):
        product1 = ProductId.generate()
        product2 = ProductId.generate()

        draft_order.add_item(
            product_id=product1,
            product_name="Product 1",
            quantity=Quantity(2),
            unit_price=Money.from_string("10.00", "USD"),
        )

        draft_order.add_item(
            product_id=product2,
            product_name="Product 2",
            quantity=Quantity(1),
            unit_price=Money.from_string("25.00", "USD"),
        )

        # Total should be (2 * 10) + (1 * 25) = 45
        assert draft_order.total == Money.from_string("45.00", "USD")

    def test_version_incremented_on_persistence(self, draft_order):
        initial_version = draft_order.version
        draft_order.increment_version()
        assert draft_order.version == initial_version + 1


class TestDomainEvents:
    """Test domain event collection"""

    def test_collect_events_returns_all_events(self, draft_order, product_id):
        # Create order raises 1 event
        # Add item raises 1 event
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )

        events = draft_order.collect_events()
        assert len(events) == 2
        assert isinstance(events[0], OrderCreated)
        assert isinstance(events[1], LineItemAdded)

    def test_collect_events_clears_event_list(self, draft_order, product_id):
        draft_order.add_item(
            product_id=product_id,
            product_name="Test Product",
            quantity=Quantity(1),
            unit_price=Money.from_string("10.00", "USD"),
        )

        first_collect = draft_order.collect_events()
        assert len(first_collect) > 0

        second_collect = draft_order.collect_events()
        assert len(second_collect) == 0  # Events cleared after first collect
