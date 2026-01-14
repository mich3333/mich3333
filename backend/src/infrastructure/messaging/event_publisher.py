"""
Event Publisher implementations.

Publishes domain events to subscribers/message bus.
"""
import json
import logging
from typing import List, Protocol
from datetime import datetime

from ...domain.shared.domain_event import DomainEvent


logger = logging.getLogger(__name__)


class EventPublisher(Protocol):
    """Protocol for event publishing"""

    async def publish_events(self, events: List[DomainEvent]) -> None:
        """Publish domain events"""
        ...


class InMemoryEventPublisher:
    """
    Simple in-memory event publisher.

    Just logs events for now. In production, you'd use Redis Pub/Sub,
    RabbitMQ, Kafka, etc.
    """

    def __init__(self):
        self.published_events: List[DomainEvent] = []

    async def publish_events(self, events: List[DomainEvent]) -> None:
        """Publish events (currently just logs and stores in memory)"""
        for event in events:
            # Serialize event for logging
            event_data = {
                "event_id": str(event.event_id),
                "event_type": event.event_type,
                "occurred_at": event.occurred_at.isoformat(),
                # Add more fields from the specific event...
            }

            logger.info(
                f"📣 Event published: {event.event_type}",
                extra={"event": event_data}
            )

            # Store in memory (useful for testing)
            self.published_events.append(event)

    def clear(self) -> None:
        """Clear published events (for testing)"""
        self.published_events.clear()

    def get_published_events(self) -> List[DomainEvent]:
        """Get all published events (for testing)"""
        return self.published_events.copy()


class LoggingEventPublisher:
    """
    Event publisher that just logs events.

    Useful for development and debugging.
    """

    async def publish_events(self, events: List[DomainEvent]) -> None:
        """Log events"""
        for event in events:
            logger.info(
                f"📣 Domain Event: {event.event_type}",
                extra={
                    "event_id": str(event.event_id),
                    "event_type": event.event_type,
                    "occurred_at": event.occurred_at.isoformat(),
                }
            )


# TODO: Implement RedisEventPublisher for production
# class RedisEventPublisher:
#     """
#     Event publisher using Redis Streams.
#
#     Publishes events to Redis for downstream consumers.
#     """
#     def __init__(self, redis_client):
#         self.redis = redis_client
#
#     async def publish_events(self, events: List[DomainEvent]) -> None:
#         """Publish events to Redis Stream"""
#         for event in events:
#             await self.redis.xadd(
#                 "domain_events",
#                 {
#                     "event_id": str(event.event_id),
#                     "event_type": event.event_type,
#                     "payload": json.dumps(event.__dict__),
#                 }
#             )
