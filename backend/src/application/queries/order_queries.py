"""
Queries for reading Order data.

Queries retrieve data without modifying system state (CQRS pattern).
"""
from dataclasses import dataclass

from ...domain.order.value_objects.ids import OrderId, CustomerId


@dataclass(frozen=True)
class GetOrderQuery:
    """Query to get a single order by ID"""
    order_id: OrderId


@dataclass(frozen=True)
class ListCustomerOrdersQuery:
    """Query to list all orders for a customer"""
    customer_id: CustomerId
    limit: int = 100
    offset: int = 0
