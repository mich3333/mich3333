"""
ID value objects for Order domain.

Strongly-typed IDs prevent mixing up different entity types.
"""
from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Union


@dataclass(frozen=True)
class OrderId:
    """Strongly-typed Order ID"""
    value: UUID

    @classmethod
    def generate(cls) -> "OrderId":
        """Generate new Order ID"""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "OrderId":
        """Parse from string"""
        return cls(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class LineItemId:
    """Strongly-typed LineItem ID"""
    value: UUID

    @classmethod
    def generate(cls) -> "LineItemId":
        """Generate new LineItem ID"""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "LineItemId":
        """Parse from string"""
        return cls(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class CustomerId:
    """Strongly-typed Customer ID"""
    value: UUID

    @classmethod
    def generate(cls) -> "CustomerId":
        """Generate new Customer ID"""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "CustomerId":
        """Parse from string"""
        return cls(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class ProductId:
    """Strongly-typed Product ID"""
    value: UUID

    @classmethod
    def generate(cls) -> "ProductId":
        """Generate new Product ID"""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "ProductId":
        """Parse from string"""
        return cls(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class PaymentId:
    """Strongly-typed Payment ID"""
    value: UUID

    @classmethod
    def generate(cls) -> "PaymentId":
        """Generate new Payment ID"""
        return cls(uuid4())

    @classmethod
    def from_string(cls, id_str: str) -> "PaymentId":
        """Parse from string"""
        return cls(UUID(id_str))

    def __str__(self) -> str:
        return str(self.value)
