"""
LineItem entity.

Part of the Order aggregate. Cannot exist independently of an Order.
"""
from decimal import Decimal

from ..value_objects.ids import LineItemId, ProductId
from ..value_objects.money import Money
from ..value_objects.address import Quantity


class LineItem:
    """
    LineItem entity within Order aggregate.

    Represents a single line in an order (product + quantity).
    """

    def __init__(
        self,
        id: LineItemId,
        product_id: ProductId,
        product_name: str,
        quantity: Quantity,
        unit_price: Money,
    ):
        self._id = id
        self._product_id = product_id
        self._product_name = product_name
        self._quantity = quantity
        self._unit_price = unit_price

    @property
    def id(self) -> LineItemId:
        return self._id

    @property
    def product_id(self) -> ProductId:
        return self._product_id

    @property
    def product_name(self) -> str:
        return self._product_name

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def unit_price(self) -> Money:
        return self._unit_price

    def subtotal(self) -> Money:
        """Calculate subtotal for this line item"""
        return self._unit_price * Decimal(self._quantity.value)

    def increase_quantity(self, additional_quantity: Quantity) -> None:
        """Increase quantity by specified amount"""
        self._quantity = self._quantity + additional_quantity

    def update_quantity(self, new_quantity: Quantity) -> None:
        """Update quantity to specified amount"""
        self._quantity = new_quantity

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LineItem):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

    def __repr__(self) -> str:
        return (
            f"LineItem(id={self._id}, product_id={self._product_id}, "
            f"quantity={self._quantity}, unit_price={self._unit_price})"
        )
