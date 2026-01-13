"""
Domain Entity and Aggregate Root base classes.

Entities have identity - two entities with same attributes but different IDs
are different entities.

Aggregate Roots are entities that enforce consistency boundaries.
"""
from abc import ABC
from typing import List
from uuid import UUID

from .domain_event import DomainEvent


class Entity(ABC):
    """
    Base class for entities.

    Entities are defined by their identity, not their attributes.
    """

    def __init__(self, id: UUID):
        self._id = id

    @property
    def id(self) -> UUID:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(Entity):
    """
    Base class for aggregate roots.

    Aggregate roots:
    - Are the only entry point to the aggregate
    - Enforce all invariants
    - Raise domain events
    - Control transactional boundaries
    """

    def __init__(self, id: UUID, version: int = 0):
        super().__init__(id)
        self._version = version
        self._events: List[DomainEvent] = []

    @property
    def version(self) -> int:
        """Version for optimistic locking"""
        return self._version

    def _raise_event(self, event: DomainEvent) -> None:
        """Add domain event to be published after persistence"""
        self._events.append(event)

    def collect_events(self) -> List[DomainEvent]:
        """Collect and clear events (called after persistence)"""
        events = self._events.copy()
        self._events.clear()
        return events

    def increment_version(self) -> None:
        """Increment version (called after successful persistence)"""
        self._version += 1
