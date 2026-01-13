"""
Address value object.

Represents a physical shipping/billing address.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Address:
    """
    Immutable address value object.

    Simplified version - real system would have more validation
    (postal code format, country codes, etc.)
    """
    street: str
    city: str
    state: str
    postal_code: str
    country: str

    def __post_init__(self):
        # Basic validation
        if not self.street or not self.street.strip():
            raise ValueError("Street address is required")
        if not self.city or not self.city.strip():
            raise ValueError("City is required")
        if not self.state or not self.state.strip():
            raise ValueError("State is required")
        if not self.postal_code or not self.postal_code.strip():
            raise ValueError("Postal code is required")
        if not self.country or not self.country.strip():
            raise ValueError("Country is required")

        # Normalize strings
        object.__setattr__(self, 'street', self.street.strip())
        object.__setattr__(self, 'city', self.city.strip())
        object.__setattr__(self, 'state', self.state.strip().upper())
        object.__setattr__(self, 'postal_code', self.postal_code.strip())
        object.__setattr__(self, 'country', self.country.strip().upper())

    def __str__(self) -> str:
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}, {self.country}"


@dataclass(frozen=True)
class Quantity:
    """
    Quantity value object.

    Represents a positive integer quantity.
    """
    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise TypeError("Quantity must be an integer")
        if self.value <= 0:
            raise ValueError("Quantity must be positive")

    def __add__(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value + other.value)

    def __mul__(self, multiplier: int) -> "Quantity":
        if not isinstance(multiplier, int):
            raise TypeError("Can only multiply Quantity by int")
        return Quantity(self.value * multiplier)

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)
