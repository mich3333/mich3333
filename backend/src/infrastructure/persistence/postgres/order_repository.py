"""
PostgreSQL implementation of OrderRepository.

Maps between domain Order aggregate and SQLAlchemy ORM models.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ....domain.order.aggregates.order import Order
from ....domain.order.aggregates.line_item import LineItem
from ....domain.order.repositories import OrderRepository
from ....domain.order.value_objects.ids import (
    OrderId,
    CustomerId,
    ProductId,
    LineItemId,
    PaymentId,
)
from ....domain.order.value_objects.money import Money
from ....domain.order.value_objects.address import Address, Quantity
from ....domain.order.value_objects.order_status import OrderStatus
from ....domain.order.exceptions import ConcurrencyError, OrderNotFoundError

from .models import OrderModel, LineItemModel


class PostgresOrderRepository(OrderRepository):
    """
    PostgreSQL implementation of OrderRepository using SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, order: Order) -> None:
        """
        Save an order (create or update).

        Handles optimistic locking using version field.
        """
        # Check if order exists (no eager loading for update check)
        stmt = select(OrderModel).where(OrderModel.id == order.order_id.value)
        result = await self.session.execute(stmt)
        existing_model = result.unique().scalar_one_or_none()

        if existing_model:
            # UPDATE - check version for optimistic locking
            if existing_model.version != order.version:
                raise ConcurrencyError(
                    f"Order {order.order_id} has been modified by another transaction. "
                    f"Expected version {order.version}, found {existing_model.version}"
                )

            # Update existing model
            self._update_model_from_aggregate(existing_model, order)
            order.increment_version()
        else:
            # CREATE - insert new model
            new_model = self._aggregate_to_model(order)
            self.session.add(new_model)
            order.increment_version()

        await self.session.flush()

    async def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Find an order by its ID."""
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.line_items))
            .where(OrderModel.id == order_id.value)
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalar_one_or_none()

        if not model:
            return None

        return self._model_to_aggregate(model)

    async def find_by_customer_id(
        self,
        customer_id: CustomerId,
        limit: int = 100,
        offset: int = 0
    ) -> List[Order]:
        """Find all orders for a customer."""
        stmt = (
            select(OrderModel)
            .options(selectinload(OrderModel.line_items))
            .where(OrderModel.customer_id == customer_id.value)
            .order_by(OrderModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.unique().scalars().all()

        return [self._model_to_aggregate(model) for model in models]

    async def delete(self, order_id: OrderId) -> None:
        """Delete an order."""
        stmt = select(OrderModel).where(OrderModel.id == order_id.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            raise OrderNotFoundError(f"Order {order_id} not found")

        await self.session.delete(model)
        await self.session.flush()

    async def exists(self, order_id: OrderId) -> bool:
        """Check if an order exists."""
        stmt = select(OrderModel.id).where(OrderModel.id == order_id.value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    # ========== Private mapping methods ==========

    def _aggregate_to_model(self, order: Order) -> OrderModel:
        """Convert Order aggregate to OrderModel."""
        model = OrderModel(
            id=order.order_id.value,
            customer_id=order.customer_id.value,
            status=order.status.value,
            total_amount=order.total.amount,
            total_currency=order.total.currency,
            # Shipping address
            shipping_street=order.shipping_address.street,
            shipping_city=order.shipping_address.city,
            shipping_state=order.shipping_address.state,
            shipping_postal_code=order.shipping_address.postal_code,
            shipping_country=order.shipping_address.country,
            # Billing address
            billing_street=order.billing_address.street,
            billing_city=order.billing_address.city,
            billing_state=order.billing_address.state,
            billing_postal_code=order.billing_address.postal_code,
            billing_country=order.billing_address.country,
            # Timestamps
            created_at=order.created_at,
            updated_at=order.updated_at,
            submitted_at=getattr(order, '_submitted_at', None),
            payment_confirmed_at=getattr(order, '_payment_confirmed_at', None),
            processing_started_at=getattr(order, '_processing_started_at', None),
            shipped_at=getattr(order, '_shipped_at', None),
            delivered_at=getattr(order, '_delivered_at', None),
            cancelled_at=getattr(order, '_cancelled_at', None),
            # Tracking
            tracking_number=getattr(order, '_tracking_number', None),
            payment_id=getattr(order, '_payment_id', None).value if hasattr(order, '_payment_id') and getattr(order, '_payment_id') else None,
            # Version
            version=order.version,
        )

        # Add line items
        for line_item in order.line_items:
            line_item_model = self._line_item_to_model(line_item, order.order_id.value)
            model.line_items.append(line_item_model)

        return model

    def _update_model_from_aggregate(self, model: OrderModel, order: Order) -> None:
        """Update existing OrderModel from Order aggregate."""
        # Update scalar fields
        model.status = order.status.value
        model.total_amount = order.total.amount
        model.total_currency = order.total.currency
        model.updated_at = order.updated_at
        model.submitted_at = getattr(order, '_submitted_at', None)
        model.payment_confirmed_at = getattr(order, '_payment_confirmed_at', None)
        model.processing_started_at = getattr(order, '_processing_started_at', None)
        model.shipped_at = getattr(order, '_shipped_at', None)
        model.delivered_at = getattr(order, '_delivered_at', None)
        model.cancelled_at = getattr(order, '_cancelled_at', None)
        model.tracking_number = getattr(order, '_tracking_number', None)
        model.payment_id = getattr(order, '_payment_id', None).value if hasattr(order, '_payment_id') and getattr(order, '_payment_id') else None
        model.version = order.version + 1  # Will be incremented

        # Update line items (simple strategy: delete all and re-add)
        # In production, you might want a more sophisticated sync algorithm
        model.line_items.clear()
        for line_item in order.line_items:
            line_item_model = self._line_item_to_model(line_item, order.order_id.value)
            model.line_items.append(line_item_model)

    def _line_item_to_model(self, line_item: LineItem, order_id: UUID) -> LineItemModel:
        """Convert LineItem entity to LineItemModel."""
        return LineItemModel(
            id=line_item.id.value,
            order_id=order_id,
            product_id=line_item.product_id.value,
            quantity=line_item.quantity.value,
            unit_price_amount=line_item.unit_price.amount,
            unit_price_currency=line_item.unit_price.currency,
        )

    def _model_to_aggregate(self, model: OrderModel) -> Order:
        """Convert OrderModel to Order aggregate."""
        # Convert line items
        line_items = [
            LineItem(
                id=LineItemId(item.id),
                product_id=ProductId(item.product_id),
                product_name="Product",  # TODO: fetch from product catalog
                quantity=Quantity(item.quantity),
                unit_price=Money(item.unit_price_amount, item.unit_price_currency),
            )
            for item in model.line_items
        ]

        # Reconstruct order
        order = Order(
            id=OrderId(model.id),
            customer_id=CustomerId(model.customer_id),
            status=OrderStatus(model.status),
            line_items=line_items,
            shipping_address=Address(
                street=model.shipping_street,
                city=model.shipping_city,
                state=model.shipping_state,
                postal_code=model.shipping_postal_code,
                country=model.shipping_country,
            ),
            billing_address=Address(
                street=model.billing_street,
                city=model.billing_city,
                state=model.billing_state,
                postal_code=model.billing_postal_code,
                country=model.billing_country,
            ),
            total=Money(model.total_amount, model.total_currency),
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )

        # Set optional timestamps using private attributes (reconstitution)
        if model.submitted_at:
            order._submitted_at = model.submitted_at
        if model.payment_confirmed_at:
            order._payment_confirmed_at = model.payment_confirmed_at
        if model.processing_started_at:
            order._processing_started_at = model.processing_started_at
        if model.shipped_at:
            order._shipped_at = model.shipped_at
        if model.delivered_at:
            order._delivered_at = model.delivered_at
        if model.cancelled_at:
            order._cancelled_at = model.cancelled_at
        if model.tracking_number:
            order._tracking_number = model.tracking_number
        if model.payment_id:
            order._payment_id = PaymentId(model.payment_id)

        return order
