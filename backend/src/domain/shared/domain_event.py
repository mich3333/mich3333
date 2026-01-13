"""
Domain Event base class.

Domain events represent something that happened in the domain that domain
experts care about. They are named in past tense (OrderSubmitted, PaymentConfirmed).

Events are immutable and contain all the information needed by subscribers.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from uuid import UUID, uuid4


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    All events must be:
    - Immutable (frozen=True)
    - Serializable (use primitive types)
    - Self-contained (include all necessary data)
    """
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    # Event type for serialization/routing
    event_type: ClassVar[str]

    def __post_init__(self):
        # Ensure event_type is set by subclasses
        if not hasattr(self.__class__, 'event_type'):
            raise TypeError(
                f"{self.__class__.__name__} must define event_type class variable"
            )
