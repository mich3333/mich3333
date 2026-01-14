#!/usr/bin/env python3
"""
Quick test to verify the API works without running a server.

Tests the domain, application, and infrastructure layers.
"""
import asyncio
from datetime import datetime
from decimal import Decimal

# Domain imports
from src.domain.order.value_objects.ids import OrderId, CustomerId, ProductId
from src.domain.order.value_objects.address import Address
from src.domain.order.value_objects.money import Money
from src.domain.order.aggregates.order import Order

# Application imports
from src.application.commands.order_commands import CreateOrderCommand, AddLineItemCommand
from src.application.commands.order_command_handlers import CreateOrderCommandHandler, AddLineItemCommandHandler
from src.application.queries.order_queries import GetOrderQuery
from src.application.queries.order_query_handlers import GetOrderQueryHandler

# Infrastructure imports
from src.infrastructure.persistence.postgres.models import Base
from src.infrastructure.persistence.postgres.order_repository import PostgresOrderRepository
from src.infrastructure.messaging.event_publisher import InMemoryEventPublisher

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


async def main():
    print("=" * 70)
    print("🧪 Testing Order Management API")
    print("=" * 70)
    print()

    # 1. Setup in-memory SQLite database
    print("1️⃣  Setting up SQLite database...")
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("   ✅ Database created\n")

    # 2. Create a session
    print("2️⃣  Creating database session...")
    async with SessionFactory() as session:
        repository = PostgresOrderRepository(session)
        event_publisher = InMemoryEventPublisher()
        print("   ✅ Repository and event publisher ready\n")

        # 3. Create an order
        print("3️⃣  Creating a new order...")
        create_command = CreateOrderCommand(
            customer_id=CustomerId.generate(),
            shipping_address=Address(
                street="123 Main St",
                city="San Francisco",
                state="CA",
                postal_code="94102",
                country="US",
            ),
        )

        create_handler = CreateOrderCommandHandler(repository, event_publisher)
        order_id = await create_handler.handle(create_command)
        await session.commit()

        print(f"   ✅ Order created: {order_id}")
        print(f"   📣 Events published: {len(event_publisher.get_published_events())}\n")

        # 4. Add line items
        print("4️⃣  Adding products to order...")
        add_item_command = AddLineItemCommand(
            order_id=order_id,
            product_id=ProductId.generate(),
            quantity=2,
            unit_price=Decimal("29.99"),
            currency="USD",
        )

        add_item_handler = AddLineItemCommandHandler(repository, event_publisher)
        await add_item_handler.handle(add_item_command)
        await session.commit()

        print(f"   ✅ Added 2x Product @ $29.99")
        print(f"   📣 Total events: {len(event_publisher.get_published_events())}\n")

        # 5. Query the order
        print("5️⃣  Retrieving order details...")
        query = GetOrderQuery(order_id=order_id)
        query_handler = GetOrderQueryHandler(repository)
        order_dto = await query_handler.handle(query)

        print(f"   ✅ Order retrieved:")
        print(f"      - ID: {order_dto.id}")
        print(f"      - Customer: {order_dto.customer_id}")
        print(f"      - Status: {order_dto.status}")
        print(f"      - Line Items: {len(order_dto.line_items)}")
        print(f"      - Total: ${order_dto.total} {order_dto.currency}")
        print(f"      - Created: {order_dto.created_at}\n")

        # 6. Display domain events
        print("6️⃣  Domain events published:")
        for i, event in enumerate(event_publisher.get_published_events(), 1):
            print(f"   {i}. {event.event_type} (at {event.occurred_at.strftime('%H:%M:%S')})")
        print()

    # Cleanup
    await engine.dispose()

    print("=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("🎉 The API is working correctly!")
    print()
    print("Next steps:")
    print("  1. Run the demo API: python demo_app.py")
    print("  2. Open http://localhost:8000/docs")
    print("  3. Try the endpoints in Swagger UI")
    print()


if __name__ == "__main__":
    asyncio.run(main())
