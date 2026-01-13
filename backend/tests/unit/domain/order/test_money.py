"""
Unit tests for Money value object.

Tests demonstrate:
- Immutability
- Currency consistency enforcement
- Arithmetic operations
- Edge cases
"""
import pytest
from decimal import Decimal

from src.domain.order.value_objects.money import Money


class TestMoneyCreation:
    """Test Money instantiation and validation"""

    def test_create_money_with_decimal(self):
        money = Money(Decimal("19.99"), "USD")
        assert money.amount == Decimal("19.99")
        assert money.currency == "USD"

    def test_create_money_normalizes_currency_to_uppercase(self):
        money = Money(Decimal("10.00"), "usd")
        assert money.currency == "USD"

    def test_create_money_rounds_to_two_decimals(self):
        money = Money(Decimal("19.999"), "USD")
        assert money.amount == Decimal("20.00")

    def test_create_money_from_string(self):
        money = Money.from_string("19.99", "USD")
        assert money.amount == Decimal("19.99")
        assert money.currency == "USD"

    def test_create_zero_money(self):
        money = Money.zero("EUR")
        assert money.amount == Decimal("0.00")
        assert money.currency == "EUR"

    def test_reject_non_decimal_amount(self):
        with pytest.raises(TypeError, match="Amount must be Decimal type"):
            Money(19.99, "USD")  # Float not allowed

    def test_reject_invalid_currency_code(self):
        with pytest.raises(ValueError, match="3-letter ISO 4217 code"):
            Money(Decimal("10.00"), "US")  # Too short

    def test_reject_infinite_amount(self):
        with pytest.raises(ValueError, match="Amount must be finite"):
            Money(Decimal("Infinity"), "USD")


class TestMoneyArithmetic:
    """Test arithmetic operations"""

    def test_add_same_currency(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.50"), "USD")
        result = money1 + money2
        assert result.amount == Decimal("15.50")
        assert result.currency == "USD"

    def test_add_different_currency_raises_error(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.50"), "EUR")
        with pytest.raises(ValueError, match="different currencies"):
            money1 + money2

    def test_subtract_same_currency(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("3.50"), "USD")
        result = money1 - money2
        assert result.amount == Decimal("6.50")

    def test_multiply_by_integer(self):
        money = Money(Decimal("10.00"), "USD")
        result = money * 3
        assert result.amount == Decimal("30.00")
        assert result.currency == "USD"

    def test_multiply_by_decimal(self):
        money = Money(Decimal("10.00"), "USD")
        result = money * Decimal("1.5")
        assert result.amount == Decimal("15.00")

    def test_multiply_commutative(self):
        money = Money(Decimal("10.00"), "USD")
        result = 3 * money
        assert result.amount == Decimal("30.00")

    def test_divide_by_integer(self):
        money = Money(Decimal("10.00"), "USD")
        result = money / 2
        assert result.amount == Decimal("5.00")

    def test_divide_by_decimal(self):
        money = Money(Decimal("10.00"), "USD")
        result = money / Decimal("2.5")
        assert result.amount == Decimal("4.00")

    def test_divide_by_zero_raises_error(self):
        money = Money(Decimal("10.00"), "USD")
        with pytest.raises(ZeroDivisionError):
            money / 0


class TestMoneyComparison:
    """Test comparison operations"""

    def test_equal_same_amount_and_currency(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("10.00"), "USD")
        assert money1 == money2

    def test_not_equal_different_amount(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.00"), "USD")
        assert money1 != money2

    def test_not_equal_different_currency(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("10.00"), "EUR")
        assert money1 != money2

    def test_less_than(self):
        money1 = Money(Decimal("5.00"), "USD")
        money2 = Money(Decimal("10.00"), "USD")
        assert money1 < money2
        assert not money2 < money1

    def test_greater_than(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.00"), "USD")
        assert money1 > money2
        assert not money2 > money1

    def test_comparison_different_currency_raises_error(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = Money(Decimal("5.00"), "EUR")
        with pytest.raises(ValueError, match="different currencies"):
            money1 < money2


class TestMoneyPredicates:
    """Test predicate methods"""

    def test_is_positive(self):
        money = Money(Decimal("10.00"), "USD")
        assert money.is_positive()
        assert not Money(Decimal("-5.00"), "USD").is_positive()
        assert not Money.zero("USD").is_positive()

    def test_is_negative(self):
        money = Money(Decimal("-10.00"), "USD")
        assert money.is_negative()
        assert not Money(Decimal("5.00"), "USD").is_negative()
        assert not Money.zero("USD").is_negative()

    def test_is_zero(self):
        money = Money.zero("USD")
        assert money.is_zero()
        assert not Money(Decimal("0.01"), "USD").is_zero()

    def test_abs(self):
        money = Money(Decimal("-10.50"), "USD")
        result = money.abs()
        assert result.amount == Decimal("10.50")
        assert result.currency == "USD"


class TestMoneyImmutability:
    """Test that Money is immutable"""

    def test_cannot_modify_amount(self):
        money = Money(Decimal("10.00"), "USD")
        with pytest.raises(AttributeError):
            money.amount = Decimal("20.00")

    def test_cannot_modify_currency(self):
        money = Money(Decimal("10.00"), "USD")
        with pytest.raises(AttributeError):
            money.currency = "EUR"

    def test_operations_return_new_instance(self):
        money1 = Money(Decimal("10.00"), "USD")
        money2 = money1 + Money(Decimal("5.00"), "USD")
        assert money1.amount == Decimal("10.00")  # Original unchanged
        assert money2.amount == Decimal("15.00")  # New instance
        assert money1 is not money2


class TestMoneyStringRepresentation:
    """Test string formatting"""

    def test_str_representation(self):
        money = Money(Decimal("19.99"), "USD")
        assert str(money) == "USD 19.99"

    def test_repr_representation(self):
        money = Money(Decimal("19.99"), "USD")
        assert repr(money) == "Money(amount=Decimal('19.99'), currency='USD')"
