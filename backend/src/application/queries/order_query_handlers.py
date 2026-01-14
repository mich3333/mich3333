"""
Query Handlers for reading Order data.

Query handlers retrieve data from repositories and convert to DTOs.
"""
from typing import List, Optional

from ...domain.order.repositories import OrderRepository
from ...domain.order.aggregates.order import Order
from ...domain.order.exceptions import OrderNotFoundError

from ..dtos import OrderResponseDTO, LineItemResponseDTO, AddressDTO
from .order_queries import GetOrderQuery, ListCustomerOrdersQuery


def order_to_dto(order: Order) -> OrderResponseDTO:
    """Convert Order aggregate to DTO"""
    line_items_dto = [
        LineItemResponseDTO(
            id=str(item.id),  # LineItem.id property
            product_id=str(item.product_id),
            quantity=item.quantity.value,
            unit_price=item.unit_price.amount,
            currency=item.unit_price.currency,
            subtotal=item.subtotal().amount,
        )
        for item in order.line_items
    ]

    address_dto = AddressDTO(
        street=order.shipping_address.street,
        city=order.shipping_address.city,
        state=order.shipping_address.state,
        postal_code=order.shipping_address.postal_code,
        country=order.shipping_address.country,
    )

    return OrderResponseDTO(
        id=str(order.order_id),
        customer_id=str(order.customer_id),
        status=order.status.value,
        total=order.total.amount,
        currency=order.total.currency,
        line_items=line_items_dto,
        shipping_address=address_dto,
        created_at=order.created_at,
        submitted_at=getattr(order, '_submitted_at', None),
        payment_confirmed_at=getattr(order, '_payment_confirmed_at', None),
        shipped_at=getattr(order, '_shipped_at', None),
        delivered_at=getattr(order, '_delivered_at', None),
        cancelled_at=getattr(order, '_cancelled_at', None),
        tracking_number=getattr(order, '_tracking_number', None),
        version=order.version,
    )


class GetOrderQueryHandler:
    """Handler for GetOrderQuery"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def handle(self, query: GetOrderQuery) -> OrderResponseDTO:
        """Get a single order by ID"""
        order = await self.order_repository.find_by_id(query.order_id)
        if not order:
            raise OrderNotFoundError(f"Order {query.order_id} not found")

        return order_to_dto(order)


class ListCustomerOrdersQueryHandler:
    """Handler for ListCustomerOrdersQuery"""

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository

    async def handle(self, query: ListCustomerOrdersQuery) -> List[OrderResponseDTO]:
        """List all orders for a customer"""
        orders = await self.order_repository.find_by_customer_id(
            customer_id=query.customer_id,
            limit=query.limit,
            offset=query.offset,
        )

        return [order_to_dto(order) for order in orders]
