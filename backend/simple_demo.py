#!/usr/bin/env python3
"""
Simplified demo - just test the core functionality without FastAPI complexity.

This shows the complete order workflow end-to-end.
"""
import asyncio
from decimal import Decimal
from datetime import datetime

from src.domain.order.value_objects.ids import OrderId, CustomerId, ProductId
from src.domain.order.value_objects.address import Address
from src.application.commands.order_commands import (
    CreateOrderCommand,
    AddLineItemCommand,
    SubmitOrderCommand,
    ConfirmPaymentCommand,
    ShipOrderCommand,
)
from src.application.commands.order_command_handlers import (
    CreateOrderCommandHandler,
    AddLineItemCommandHandler,
    SubmitOrderCommandHandler,
    ConfirmPaymentCommandHandler,
    ShipOrderCommandHandler,
)
from src.application.queries.order_queries import GetOrderQuery
from src.application.queries.order_query_handlers import GetOrderQueryHandler
from src.infrastructure.persistence.postgres.models import Base
from src.infrastructure.persistence.postgres.order_repository import PostgresOrderRepository
from src.infrastructure.messaging.event_publisher import InMemoryEventPublisher

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


async def main():
    print("=" * 80)
    print("🛒 Complete Order Workflow Demo")
    print("=" * 80)
    print()

    # Setup database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session and dependencies
    async with SessionFactory() as session:
        repository = PostgresOrderRepository(session)
        event_publisher = InMemoryEventPublisher()

        # 1. Create Order
        print("📝 Step 1: Creating Order...")
        customer_id = CustomerId.generate()
        create_cmd = CreateOrderCommand(
            customer_id=customer_id,
            shipping_address=Address(
                street="456 Tech Lane",
                city="San Francisco",
                state="CA",
                postal_code="94105",
                country="US",
            ),
        )

        create_handler = CreateOrderCommandHandler(repository, event_publisher)
        order_id = await create_handler.handle(create_cmd)
        await session.commit()

        print(f"   ✅ Order created: {order_id}")
        print()

        # 2. Add Products
        print("🛍️  Step 2: Adding Products...")

        # Add product 1
        add_item1 = AddLineItemCommand(
            order_id=order_id,
            product_id=ProductId.generate(),
            quantity=2,
            unit_price=Decimal("49.99"),
            currency="USD",
        )
        add_handler = AddLineItemCommandHandler(repository, event_publisher)
        await add_handler.handle(add_item1)
        await session.commit()
        print("   ✅ Added 2x Product A @ $49.99")

        # Add product 2
        add_item2 = AddLineItemCommand(
            order_id=order_id,
            product_id=ProductId.generate(),
            quantity=1,
            unit_price=Decimal("99.99"),
            currency="USD",
        )
        await add_handler.handle(add_item2)
        await session.commit()
        print("   ✅ Added 1x Product B @ $99.99")
        print()

        # 3. View Order
        print("👀 Step 3: Viewing Order...")
        query_handler = GetOrderQueryHandler(repository)
        order = await query_handler.handle(GetOrderQuery(order_id=order_id))

        print(f"   Order ID: {order.id}")
        print(f"   Status: {order.status.upper()}")
        print(f"   Line Items: {len(order.line_items)}")
        for i, item in enumerate(order.line_items, 1):
            print(f"      {i}. Product {item.product_id[:8]}... × {item.quantity} @ ${item.unit_price}")
        print(f"   Total: ${order.total} {order.currency}")
        print()

        # 4. Submit Order
        print("📤 Step 4: Submitting Order...")
        submit_handler = SubmitOrderCommandHandler(repository, event_publisher)
        await submit_handler.handle(SubmitOrderCommand(order_id=order_id))
        await session.commit()
        print("   ✅ Order submitted for payment")
        print()

        # 5. Confirm Payment
        print("💳 Step 5: Confirming Payment...")
        from src.domain.order.value_objects.ids import PaymentId

        payment_handler = ConfirmPaymentCommandHandler(repository, event_publisher)
        await payment_handler.handle(
            ConfirmPaymentCommand(
                order_id=order_id,
                payment_id=PaymentId.generate(),
                amount_paid=Decimal("199.97"),
                currency="USD",
            )
        )
        await session.commit()
        print("   ✅ Payment confirmed")
        print()

        # 6. Start Processing
        print("⚙️  Step 6: Starting Order Processing...")
        order_entity = await repository.find_by_id(order_id)
        order_entity.start_processing()
        await repository.save(order_entity)
        await session.commit()
        events_after_processing = order_entity.collect_events()
        await event_publisher.publish_events(events_after_processing)
        print("   ✅ Order is now being processed")
        print()

        # 7. Ship Order
        print("📦 Step 7: Shipping Order...")
        ship_handler = ShipOrderCommandHandler(repository, event_publisher)
        await ship_handler.handle(
            ShipOrderCommand(
                order_id=order_id,
                tracking_number="TRACK123456789",
                carrier="UPS",
            )
        )
        await session.commit()
        print("   ✅ Order shipped")
        print("   Tracking: TRACK123456789 (UPS)")
        print()

        # 8. Final Status
        print("🎯 Final Order Status:")
        final_order = await query_handler.handle(GetOrderQuery(order_id=order_id))
        print(f"   Status: {final_order.status.upper()}")
        print(f"   Total: ${final_order.total} {final_order.currency}")
        print(f"   Tracking: {final_order.tracking_number}")
        print()

        # 8. Events Summary
        print("📣 Domain Events Published:")
        events = event_publisher.get_published_events()
        for i, event in enumerate(events, 1):
            time_str = event.occurred_at.strftime("%H:%M:%S")
            print(f"   {i}. {event.event_type} (at {time_str})")
        print()

    await engine.dispose()

    print("=" * 80)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("🎉 The Order Management System is fully functional!")
    print()
    print("What this demonstrates:")
    print("  ✅ Domain-Driven Design (Order aggregate with invariants)")
    print("  ✅ CQRS Pattern (Commands for writes, Queries for reads)")
    print("  ✅ Event-Driven Architecture (Domain events published)")
    print("  ✅ Repository Pattern (SQLAlchemy ORM with PostgreSQL-compatible code)")
    print("  ✅ Hexagonal Architecture (Clean separation of concerns)")
    print()
    print("Complete order lifecycle:")
    print("  DRAFT → PENDING_PAYMENT → CONFIRMED → PROCESSING → SHIPPED")
    print()


if __name__ == "__main__":
    asyncio.run(main())
