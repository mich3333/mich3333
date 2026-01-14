"""
Command Handlers for Order operations.

Handlers orchestrate domain operations and persistence.
They are the use cases / application services.
"""
from typing import Protocol

from ...domain.order.aggregates.order import Order
from ...domain.order.repositories import OrderRepository
from ...domain.order.value_objects.money import Money
from ...domain.order.value_objects.ids import OrderId
from ...domain.order.exceptions import OrderNotFoundError

from .order_commands import (
    CreateOrderCommand,
    AddLineItemCommand,
    UpdateLineItemQuantityCommand,
    RemoveLineItemCommand,
    SubmitOrderCommand,
    ConfirmPaymentCommand,
    ShipOrderCommand,
    DeliverOrderCommand,
    CancelOrderCommand,
)


class EventPublisher(Protocol):
    """Protocol for event publishing (dependency inversion)"""

    async def publish_events(self, events: list) -> None:
        """Publish domain events"""
        ...


class CreateOrderCommandHandler:
    """Handler for CreateOrderCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: CreateOrderCommand) -> OrderId:
        """
        Create a new order in DRAFT status.

        Returns:
            OrderId of the created order
        """
        # Generate new order ID
        order_id = OrderId.generate()

        # Create order using domain factory
        order = Order.create(
            order_id=order_id,
            customer_id=command.customer_id,
            shipping_address=command.shipping_address,
            billing_address=command.shipping_address,  # Use same address for now
        )

        # Persist order
        await self.order_repository.save(order)

        # Publish domain events
        events = order.collect_events()
        await self.event_publisher.publish_events(events)

        return order_id


class AddLineItemCommandHandler:
    """Handler for AddLineItemCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: AddLineItemCommand) -> None:
        """Add a line item to an order"""
        # Load order
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        # Execute domain operation
        unit_price = Money(command.unit_price, command.currency)
        order.add_item(
            product_id=command.product_id,
            quantity=command.quantity,
            unit_price=unit_price,
        )

        # Persist changes
        await self.order_repository.save(order)

        # Publish events
        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class UpdateLineItemQuantityCommandHandler:
    """Handler for UpdateLineItemQuantityCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: UpdateLineItemQuantityCommand) -> None:
        """Update line item quantity"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.update_item_quantity(
            line_item_id=command.line_item_id,
            new_quantity=command.new_quantity,
        )

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class RemoveLineItemCommandHandler:
    """Handler for RemoveLineItemCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: RemoveLineItemCommand) -> None:
        """Remove a line item from an order"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.remove_item(line_item_id=command.line_item_id)

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class SubmitOrderCommandHandler:
    """Handler for SubmitOrderCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: SubmitOrderCommand) -> None:
        """Submit an order for payment"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.submit()

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class ConfirmPaymentCommandHandler:
    """Handler for ConfirmPaymentCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: ConfirmPaymentCommand) -> None:
        """Confirm payment for an order"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.confirm_payment(payment_id=command.payment_id)

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class ShipOrderCommandHandler:
    """Handler for ShipOrderCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: ShipOrderCommand) -> None:
        """Ship an order"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.ship(
            tracking_number=command.tracking_number,
            carrier=command.carrier,
        )

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class DeliverOrderCommandHandler:
    """Handler for DeliverOrderCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: DeliverOrderCommand) -> None:
        """Mark an order as delivered"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.deliver()

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)


class CancelOrderCommandHandler:
    """Handler for CancelOrderCommand"""

    def __init__(
        self,
        order_repository: OrderRepository,
        event_publisher: EventPublisher,
    ):
        self.order_repository = order_repository
        self.event_publisher = event_publisher

    async def handle(self, command: CancelOrderCommand) -> None:
        """Cancel an order"""
        order = await self.order_repository.find_by_id(command.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {command.order_id} not found")

        order.cancel()

        await self.order_repository.save(order)

        events = order.collect_events()
        await self.event_publisher.publish_events(events)
