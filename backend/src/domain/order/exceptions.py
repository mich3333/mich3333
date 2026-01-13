"""
Domain exceptions for Order bounded context.

Exceptions represent business rule violations, not technical errors.
"""


class OrderDomainException(Exception):
    """Base exception for Order domain"""
    pass


class InvalidStateTransitionError(OrderDomainException):
    """Attempted invalid state transition"""
    pass


class OrderNotModifiableError(OrderDomainException):
    """Attempted to modify order that cannot be modified"""
    pass


class OrderNotCancellableError(OrderDomainException):
    """Attempted to cancel order that cannot be cancelled"""
    pass


class EmptyOrderError(OrderDomainException):
    """Attempted operation on order with no line items"""
    pass


class MinimumOrderValueError(OrderDomainException):
    """Order does not meet minimum value requirement"""
    pass


class InvalidQuantityError(OrderDomainException):
    """Invalid quantity specified"""
    pass


class ProductNotInOrderError(OrderDomainException):
    """Referenced product not found in order"""
    pass


class DuplicateLineItemError(OrderDomainException):
    """Attempted to add duplicate line item"""
    pass
