"""
FastAPI routes for Order management.

RESTful API endpoints for order operations.
"""
from typing import List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....domain.order.value_objects.ids import OrderId, CustomerId, ProductId, LineItemId, PaymentId
from ....domain.order.value_objects.address import Address
from ....domain.order.exceptions import (
    OrderDomainException,
    OrderNotFoundError,
    InvalidStateTransitionError,
    OrderNotModifiableError,
)
from ....application.commands import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
    AddLineItemCommand,
    AddLineItemCommandHandler,
    RemoveLineItemCommand,
    RemoveLineItemCommandHandler,
    SubmitOrderCommand,
    SubmitOrderCommandHandler,
    ConfirmPaymentCommand,
    ConfirmPaymentCommandHandler,
    ShipOrderCommand,
    ShipOrderCommandHandler,
    CancelOrderCommand,
    CancelOrderCommandHandler,
)
from ....application.queries import (
    GetOrderQuery,
    GetOrderQueryHandler,
    ListCustomerOrdersQuery,
    ListCustomerOrdersQueryHandler,
)
from ....application.dtos import OrderResponseDTO
from ....infrastructure.persistence.postgres import (
    PostgresOrderRepository,
    get_db_session,
)
from ....infrastructure.messaging.event_publisher import InMemoryEventPublisher


router = APIRouter(prefix="/api/orders", tags=["orders"])


# ========== Pydantic Request/Response Models ==========

class AddressRequest(BaseModel):
    """Request model for address"""
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=2, max_length=50)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=2, max_length=2)


class CreateOrderRequest(BaseModel):
    """Request model for creating an order"""
    customer_id: str = Field(..., description="Customer UUID")
    shipping_address: AddressRequest


class AddLineItemRequest(BaseModel):
    """Request model for adding a line item"""
    product_id: str = Field(..., description="Product UUID")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")


class RemoveLineItemRequest(BaseModel):
    """Request model for removing a line item"""
    line_item_id: str = Field(..., description="LineItem UUID")


class ConfirmPaymentRequest(BaseModel):
    """Request model for confirming payment"""
    payment_id: str = Field(..., description="Payment UUID")
    amount_paid: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")


class ShipOrderRequest(BaseModel):
    """Request model for shipping an order"""
    tracking_number: str = Field(..., min_length=1)
    carrier: str | None = None


class OrderResponse(BaseModel):
    """Response model for order"""
    id: str
    customer_id: str
    status: str
    total: Decimal
    currency: str
    created_at: str

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    message: str
    details: dict | None = None


# ========== Dependency Injection ==========

def get_event_publisher():
    """Get event publisher instance"""
    return InMemoryEventPublisher()


def get_order_repository(
    session: AsyncSession = Depends(get_db_session)
) -> PostgresOrderRepository:
    """Get order repository instance"""
    return PostgresOrderRepository(session)


# ========== API Endpoints ==========

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description="Create a new order in DRAFT status",
)
async def create_order(
    request: CreateOrderRequest,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Create a new order"""
    try:
        # Convert request to command
        command = CreateOrderCommand(
            customer_id=CustomerId.from_string(request.customer_id),
            shipping_address=Address(
                street=request.shipping_address.street,
                city=request.shipping_address.city,
                state=request.shipping_address.state,
                postal_code=request.shipping_address.postal_code,
                country=request.shipping_address.country,
            ),
        )

        # Execute command
        handler = CreateOrderCommandHandler(repository, event_publisher)
        order_id = await handler.handle(command)

        # Query the created order
        query_handler = GetOrderQueryHandler(repository)
        order_dto = await query_handler.handle(GetOrderQuery(order_id=order_id))

        return OrderResponse(
            id=order_dto.id,
            customer_id=order_dto.customer_id,
            status=order_dto.status,
            total=order_dto.total,
            currency=order_dto.currency,
            created_at=order_dto.created_at.isoformat(),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "InternalError", "message": str(e)},
        )


@router.get(
    "/{order_id}",
    response_model=OrderResponseDTO,
    summary="Get an order by ID",
)
async def get_order(
    order_id: str,
    repository: PostgresOrderRepository = Depends(get_order_repository),
):
    """Retrieve an order by its ID"""
    try:
        query = GetOrderQuery(order_id=OrderId.from_string(order_id))
        handler = GetOrderQueryHandler(repository)
        order_dto = await handler.handle(query)
        return order_dto

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)},
        )


@router.get(
    "/customers/{customer_id}",
    response_model=List[OrderResponseDTO],
    summary="List customer orders",
)
async def list_customer_orders(
    customer_id: str,
    limit: int = 100,
    offset: int = 0,
    repository: PostgresOrderRepository = Depends(get_order_repository),
):
    """List all orders for a customer"""
    try:
        query = ListCustomerOrdersQuery(
            customer_id=CustomerId.from_string(customer_id),
            limit=min(limit, 100),  # Cap at 100
            offset=max(offset, 0),
        )
        handler = ListCustomerOrdersQueryHandler(repository)
        orders = await handler.handle(query)
        return orders

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ValidationError", "message": str(e)},
        )


@router.post(
    "/{order_id}/items",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Add line item to order",
)
async def add_line_item(
    order_id: str,
    request: AddLineItemRequest,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Add a product to an order"""
    try:
        command = AddLineItemCommand(
            order_id=OrderId.from_string(order_id),
            product_id=ProductId.from_string(request.product_id),
            quantity=request.quantity,
            unit_price=request.unit_price,
            currency=request.currency,
        )

        handler = AddLineItemCommandHandler(repository, event_publisher)
        await handler.handle(command)

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except OrderNotModifiableError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "OrderNotModifiable", "message": str(e)},
        )
    except OrderDomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.__class__.__name__, "message": str(e)},
        )


@router.delete(
    "/{order_id}/items/{line_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove line item from order",
)
async def remove_line_item(
    order_id: str,
    line_item_id: str,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Remove a product from an order"""
    try:
        command = RemoveLineItemCommand(
            order_id=OrderId.from_string(order_id),
            line_item_id=LineItemId.from_string(line_item_id),
        )

        handler = RemoveLineItemCommandHandler(repository, event_publisher)
        await handler.handle(command)

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except OrderDomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.__class__.__name__, "message": str(e)},
        )


@router.post(
    "/{order_id}/submit",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Submit order for payment",
)
async def submit_order(
    order_id: str,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Submit an order for payment"""
    try:
        command = SubmitOrderCommand(order_id=OrderId.from_string(order_id))
        handler = SubmitOrderCommandHandler(repository, event_publisher)
        await handler.handle(command)

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except InvalidStateTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "InvalidStateTransition", "message": str(e)},
        )
    except OrderDomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.__class__.__name__, "message": str(e)},
        )


@router.post(
    "/{order_id}/payment",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Confirm payment for order",
)
async def confirm_payment(
    order_id: str,
    request: ConfirmPaymentRequest,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Confirm payment for an order"""
    try:
        command = ConfirmPaymentCommand(
            order_id=OrderId.from_string(order_id),
            payment_id=PaymentId.from_string(request.payment_id),
            amount_paid=request.amount_paid,
            currency=request.currency,
        )

        handler = ConfirmPaymentCommandHandler(repository, event_publisher)
        await handler.handle(command)

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except OrderDomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.__class__.__name__, "message": str(e)},
        )


@router.post(
    "/{order_id}/ship",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ship an order",
)
async def ship_order(
    order_id: str,
    request: ShipOrderRequest,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Mark an order as shipped"""
    try:
        command = ShipOrderCommand(
            order_id=OrderId.from_string(order_id),
            tracking_number=request.tracking_number,
            carrier=request.carrier,
        )

        handler = ShipOrderCommandHandler(repository, event_publisher)
        await handler.handle(command)

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except OrderDomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.__class__.__name__, "message": str(e)},
        )


@router.post(
    "/{order_id}/cancel",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel an order",
)
async def cancel_order(
    order_id: str,
    repository: PostgresOrderRepository = Depends(get_order_repository),
    event_publisher: InMemoryEventPublisher = Depends(get_event_publisher),
):
    """Cancel an order"""
    try:
        command = CancelOrderCommand(order_id=OrderId.from_string(order_id))
        handler = CancelOrderCommandHandler(repository, event_publisher)
        await handler.handle(command)

    except OrderNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "NotFound", "message": f"Order {order_id} not found"},
        )
    except OrderDomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.__class__.__name__, "message": str(e)},
        )
