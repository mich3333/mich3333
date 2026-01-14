"""
Order Repository interface (Domain Layer).

This is a port - the domain defines what it needs, infrastructure implements it.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..aggregates.order import Order
from ..value_objects.ids import OrderId, CustomerId


class OrderRepository(ABC):
    """
    Repository for Order aggregates.

    This is the domain's contract with the infrastructure layer.
    Implementations might use PostgreSQL, MongoDB, in-memory, etc.
    """

    @abstractmethod
    async def save(self, order: Order) -> None:
        """
        Save an order (create or update).

        Implementation must:
        - Persist the order atomically
        - Publish domain events after successful persistence
        - Handle optimistic locking using version
        - Update version after successful save

        Raises:
            ConcurrencyError: If version conflict detected (optimistic locking)
            RepositoryError: If persistence fails
        """
        pass

    @abstractmethod
    async def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """
        Find an order by its ID.

        Returns:
            Order if found, None otherwise
        """
        pass

    @abstractmethod
    async def find_by_customer_id(
        self,
        customer_id: CustomerId,
        limit: int = 100,
        offset: int = 0
    ) -> List[Order]:
        """
        Find all orders for a customer.

        Args:
            customer_id: Customer to search for
            limit: Maximum number of results (default 100)
            offset: Number of results to skip (for pagination)

        Returns:
            List of orders (may be empty)
        """
        pass

    @abstractmethod
    async def delete(self, order_id: OrderId) -> None:
        """
        Delete an order (soft or hard delete, implementation-dependent).

        Raises:
            OrderNotFoundError: If order doesn't exist
        """
        pass

    @abstractmethod
    async def exists(self, order_id: OrderId) -> bool:
        """
        Check if an order exists.

        Returns:
            True if order exists, False otherwise
        """
        pass
