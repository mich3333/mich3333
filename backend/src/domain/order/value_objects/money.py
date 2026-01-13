"""
Money value object.

Represents an amount of money in a specific currency.
Immutable and enforces currency consistency.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Union


@dataclass(frozen=True)
class Money:
    """
    Money value object.

    Invariants:
    - Amount must be finite
    - Currency must be valid ISO 4217 code
    - Amount stored with 2 decimal places (standard for currency)
    """
    amount: Decimal
    currency: str

    def __post_init__(self):
        # Validate and normalize amount
        if not isinstance(self.amount, Decimal):
            raise TypeError("Amount must be Decimal type")

        if not self.amount.is_finite():
            raise ValueError("Amount must be finite")

        # Normalize to 2 decimal places
        normalized = self.amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'amount', normalized)

        # Validate currency (basic check - real system would use full ISO 4217 list)
        if not isinstance(self.currency, str):
            raise TypeError("Currency must be string")

        currency_upper = self.currency.upper()
        if len(currency_upper) != 3:
            raise ValueError("Currency must be 3-letter ISO 4217 code")

        object.__setattr__(self, 'currency', currency_upper)

    @classmethod
    def zero(cls, currency: str = "USD") -> "Money":
        """Create zero money"""
        return cls(Decimal("0.00"), currency)

    @classmethod
    def from_string(cls, amount: str, currency: str = "USD") -> "Money":
        """Create from string (e.g., "19.99")"""
        return cls(Decimal(amount), currency)

    def __add__(self, other: "Money") -> "Money":
        """Add two money values"""
        self._check_currency_match(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract two money values"""
        self._check_currency_match(other)
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, multiplier: Union[int, Decimal]) -> "Money":
        """Multiply money by scalar"""
        if isinstance(multiplier, int):
            multiplier = Decimal(multiplier)
        elif not isinstance(multiplier, Decimal):
            raise TypeError("Can only multiply Money by int or Decimal")

        return Money(self.amount * multiplier, self.currency)

    def __rmul__(self, multiplier: Union[int, Decimal]) -> "Money":
        """Support scalar * Money"""
        return self.__mul__(multiplier)

    def __truediv__(self, divisor: Union[int, Decimal]) -> "Money":
        """Divide money by scalar"""
        if isinstance(divisor, int):
            divisor = Decimal(divisor)
        elif not isinstance(divisor, Decimal):
            raise TypeError("Can only divide Money by int or Decimal")

        if divisor == Decimal("0"):
            raise ZeroDivisionError("Cannot divide money by zero")

        return Money(self.amount / divisor, self.currency)

    def __lt__(self, other: "Money") -> bool:
        self._check_currency_match(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        self._check_currency_match(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        self._check_currency_match(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        self._check_currency_match(other)
        return self.amount >= other.amount

    def _check_currency_match(self, other: "Money") -> None:
        """Ensure operations only happen between same currency"""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot operate on different currencies: {self.currency} vs {other.currency}"
            )

    def is_positive(self) -> bool:
        """Check if amount is positive"""
        return self.amount > Decimal("0")

    def is_negative(self) -> bool:
        """Check if amount is negative"""
        return self.amount < Decimal("0")

    def is_zero(self) -> bool:
        """Check if amount is zero"""
        return self.amount == Decimal("0")

    def abs(self) -> "Money":
        """Get absolute value"""
        return Money(abs(self.amount), self.currency)

    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"

    def __repr__(self) -> str:
        return f"Money(amount=Decimal('{self.amount}'), currency='{self.currency}')"
