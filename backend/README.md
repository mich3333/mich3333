# Order Management System - Domain-Driven Design Implementation

**A senior-level portfolio project demonstrating Domain-Driven Design, hexagonal architecture, and modular monolith patterns.**

---

## Overview

This is a backend system for managing e-commerce orders, built from the ground up using Domain-Driven Design principles. It showcases:

- **Rich domain model** with explicit business rules and invariants
- **Hexagonal architecture** (ports & adapters) for testability and maintainability
- **Modular monolith** structure ready for potential microservices extraction
- **Event-driven architecture** for loose coupling between bounded contexts
- **Comprehensive test coverage** demonstrating TDD practices

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│   Interfaces (HTTP, CLI)            │  ← Entry points
├─────────────────────────────────────┤
│   Application (Use Cases)           │  ← Orchestration
├─────────────────────────────────────┤
│   Domain (Business Logic)           │  ← Pure business rules
├─────────────────────────────────────┤
│   Infrastructure (DB, External APIs)│  ← Technical adapters
└─────────────────────────────────────┘
```

**Dependency Rule:** Dependencies point inward. Domain layer has ZERO external dependencies.

### Domain Model

#### Order Aggregate

The core domain is the **Order** aggregate, which enforces a strict state machine:

```
DRAFT ──────> PENDING_PAYMENT ──────> CONFIRMED ──────> PROCESSING ──────> SHIPPED ──────> DELIVERED
  │
  └──────────> CANCELLED
```

**Key Invariants:**
- Order total must always equal sum of line item subtotals
- Cannot modify order after submission
- Cannot cancel order after processing starts
- Minimum order value: $5.00
- All quantities must be positive

#### Value Objects

- **Money**: Immutable, currency-aware arithmetic
- **OrderStatus**: State machine with valid transition rules
- **Address**: Validated shipping/billing addresses
- **Strongly-typed IDs**: OrderId, ProductId, CustomerId (prevent mixing)

#### Domain Events

The system publishes events for all significant business occurrences:

- `OrderCreated`, `OrderSubmitted`, `OrderCancelled`
- `LineItemAdded`, `LineItemRemoved`, `LineItemQuantityUpdated`
- `PaymentConfirmed`, `OrderShipped`, `OrderDelivered`

These events enable:
- Eventual consistency between bounded contexts
- Audit trail
- Integration with external systems

## Project Structure

```
backend/
├── src/
│   ├── domain/                    # Pure business logic (no dependencies)
│   │   ├── order/                 # Order bounded context
│   │   │   ├── aggregates/
│   │   │   │   ├── order.py              # Order aggregate root
│   │   │   │   └── line_item.py          # LineItem entity
│   │   │   ├── value_objects/
│   │   │   │   ├── money.py
│   │   │   │   ├── order_status.py
│   │   │   │   ├── ids.py
│   │   │   │   └── address.py
│   │   │   ├── events/                   # Domain events
│   │   │   ├── repositories/             # Repository interfaces (ABC)
│   │   │   └── exceptions.py
│   │   └── shared/                # Shared kernel
│   │       ├── domain_event.py
│   │       └── entity.py
│   │
│   ├── application/               # Use cases (orchestration only)
│   │   ├── commands/              # Write operations
│   │   ├── queries/               # Read operations
│   │   └── services/
│   │
│   ├── infrastructure/            # Adapters
│   │   ├── persistence/           # Database implementations
│   │   ├── messaging/             # Event bus
│   │   └── external/              # Payment gateway, email, etc.
│   │
│   └── interfaces/                # Entry points
│       ├── http/                  # REST API (FastAPI)
│       └── cli/                   # Admin commands
│
├── tests/
│   ├── unit/                      # Fast, no I/O (domain logic)
│   ├── integration/               # Database, external services
│   └── e2e/                       # Full system tests
│
├── experiments/                   # Archived experimental code
│   ├── semantic-memory/           # Original Qdrant + embeddings
│   └── multi-agent-orchestration/ # Original agent system
│
└── docs/
    ├── architecture/
    │   ├── adr/                   # Architecture Decision Records
    │   └── domain-model.md
    └── api/
```

## Design Decisions

### Why Domain-Driven Design?

**Problem:** Original system organized around technical patterns (agents, memory, orchestration) with no explicit business concepts.

**Solution:** DDD puts business concepts first. The code uses **ubiquitous language** that business stakeholders understand (Order, LineItem, submit, ship, deliver).

### Why Modular Monolith?

**Problem:** Microservices add complexity that's unnecessary for a portfolio project.

**Solution:** Modular monolith with strong boundaries. Each bounded context (Order, Catalog, Billing) is isolated and can be extracted to a microservice later if needed.

**Benefits:**
- Simpler deployment
- Stronger consistency guarantees
- Easier refactoring
- Demonstrates pragmatism

### Why Hexagonal Architecture?

**Problem:** Original system mixed business logic with infrastructure concerns.

**Solution:** Hexagonal architecture (ports & adapters) separates:
- **Domain layer**: Pure business logic (no dependencies)
- **Application layer**: Use case orchestration
- **Infrastructure layer**: Technical adapters (DB, APIs)

**Benefits:**
- Domain is 100% testable (no mocks needed)
- Can swap infrastructure (Postgres → MongoDB)
- Business rules are explicit and verifiable

### Why No AI/LLM?

**Problem:** Original system used LLMs for deterministic operations (calculate total, validate rules).

**Solution:** Removed all AI. Business logic is deterministic and fast.

**Rationale:**
- Order total: Use arithmetic, not GPT
- Payment validation: Use business rules, not AI
- State transitions: Use state machine, not LLM

**Where AI belongs:** Product recommendations, chatbots, fraud detection (non-critical, read-side).

## Key Domain Concepts

### Aggregates

An **aggregate** is a consistency boundary. The Order aggregate consists of:
- **Order** (aggregate root) - the only entry point
- **LineItems** (entities) - owned by Order, cannot exist independently

All operations go through the Order root, which enforces invariants.

### Repository Pattern

Repositories provide the illusion of an in-memory collection:

```python
# Interface (domain layer)
class OrderRepository(ABC):
    def save(self, order: Order) -> None: ...
    def find_by_id(self, order_id: OrderId) -> Optional[Order]: ...

# Implementation (infrastructure layer)
class PostgresOrderRepository(OrderRepository):
    def save(self, order: Order) -> None:
        # Transactional persistence with optimistic locking
        ...
```

### Unit of Work Pattern

Groups operations into transactions:

```python
with unit_of_work:
    order = order_repo.find_by_id(order_id)
    order.submit()
    order_repo.save(order)
    event_publisher.publish(order.collect_events())
    unit_of_work.commit()  # Atomic
```

### Domain Events

Events represent "something that happened" (past tense):

```python
@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    order_id: UUID
    customer_id: UUID
    total_amount: str
    total_currency: str
    item_count: int
    occurred_at: datetime
```

Events are:
- Immutable
- Published after successful persistence (transactional outbox)
- Consumed by other bounded contexts (Fulfillment, Billing)

## Code Quality Practices

### Type Safety

- **Type hints everywhere** (mypy strict mode compatible)
- **Strongly-typed IDs** prevent mixing OrderId with CustomerId
- **Value objects** make invalid states unrepresentable

### Testing

- **Unit tests**: Domain logic (fast, no I/O, no mocks)
- **Integration tests**: Repository implementations
- **E2E tests**: Full HTTP API

**Coverage goals:**
- Domain layer: 100%
- Application layer: >90%
- Infrastructure layer: >80%

### Error Handling

- **Domain exceptions** for business rule violations
- **Technical exceptions** for infrastructure failures
- Clear error messages with context

### Validation

- **Input validation** at system boundaries (HTTP layer)
- **Business validation** in domain layer (aggregate methods)
- **Type system** enforces correctness at compile time

## Comparison with Original System

| Aspect | Original (Experimental) | New (Production-Ready) |
|--------|-------------------------|------------------------|
| **Organization** | Agent-centric (technical) | Domain-centric (business) |
| **State Management** | Global MissionContext | Encapsulated in aggregates |
| **Memory** | Qdrant vector DB | Postgres with schema |
| **Operations** | AI-driven (non-deterministic) | Business rules (deterministic) |
| **Consistency** | Eventual (no guarantees) | Strong (ACID transactions) |
| **Testability** | Hard to test (AI dependencies) | Easy to test (pure functions) |
| **Maintainability** | Logic scattered in prompts | Logic explicit in code |
| **Performance** | Slow (LLM calls for everything) | Fast (in-memory + DB) |
| **Cost** | Expensive (GPT for CRUD) | Cheap (no AI overhead) |

## Running the Project

### Setup

```bash
# Install dependencies (using uv for speed)
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=src

# Type check
mypy src/

# Lint
ruff check src/
```

### Running Tests

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests (requires DB)
pytest tests/integration/ -v

# Full suite with coverage
pytest --cov=src --cov-report=html
```

## Future Enhancements

### Phase 2: Application Layer
- Implement PlaceOrderService
- Add PostgreSQL repository
- Transactional outbox for events

### Phase 3: HTTP API
- FastAPI REST endpoints
- OpenAPI documentation
- Authentication & authorization

### Phase 4: Event-Driven Integration
- Redis Streams event bus
- Fulfillment subscriber (stub)
- Idempotency for external calls

### Phase 5: Observability
- Structured logging (structlog)
- Metrics (Prometheus)
- Distributed tracing (OpenTelemetry)

## Learning Resources

### Domain-Driven Design
- **Book**: "Domain-Driven Design" by Eric Evans
- **Book**: "Implementing Domain-Driven Design" by Vaughn Vernon
- **Concept**: Aggregates enforce consistency boundaries

### Hexagonal Architecture
- **Pattern**: Ports & Adapters
- **Benefit**: Domain has zero dependencies
- **Test Strategy**: Test domain without mocks

### Event-Driven Architecture
- **Pattern**: Domain events for decoupling
- **Implementation**: Transactional outbox
- **Trade-off**: Eventual consistency

## Interview Discussion Points

### For Senior Backend Engineers

1. **Aggregate Design**
   - Why is Order the aggregate root?
   - What are the consistency boundaries?
   - How do we prevent concurrent updates? (Optimistic locking)

2. **State Machine**
   - Why explicit state transitions?
   - How do we prevent invalid states?
   - What happens if payment fails?

3. **Testing Strategy**
   - Why are domain tests so fast?
   - Why don't we need mocks for domain tests?
   - How do we test repository implementations?

4. **Trade-offs**
   - Monolith vs. microservices: When to split?
   - Strong vs. eventual consistency: Where is each appropriate?
   - Event sourcing: Why not from day 1?

5. **Scalability**
   - How would you scale this system?
   - What are the bottlenecks?
   - Where would you introduce caching?

## Author

**Michael Chen** - Senior Backend Engineer

This project demonstrates architectural thinking, domain modeling, and production-ready engineering practices. It was intentionally built as a **controlled reset** from an experimental agent system to showcase:

- When to use AI (recommendations) vs. when not to (transactions)
- How to design for correctness, not just features
- Pragmatic technology choices (monolith, Postgres, FastAPI)
- Professional communication through code and documentation

## License

MIT License - Feel free to use this as a learning resource or portfolio template.

---

**Note:** This is a portfolio project optimized for demonstrating senior-level engineering skills. The original experimental agent systems are archived in `/experiments` to show the evolution of the architecture.
