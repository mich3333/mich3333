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

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for PostgreSQL)
- Or: PostgreSQL 15+ installed locally

### Quick Start

```bash
# 1. Start PostgreSQL and Redis using Docker Compose
cd backend
docker-compose up -d

# 2. Install Python dependencies
pip install -e ".[dev]"

# 3. Run the API server
cd src/interfaces/http
python app.py

# Or use uvicorn directly:
uvicorn src.interfaces.http.app:app --reload

# 4. Open your browser
# - API Docs (Swagger): http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - Health Check: http://localhost:8000/health
```

### API Endpoints

**Order Management:**
```
POST   /api/orders                      # Create new order
GET    /api/orders/{order_id}           # Get order details
GET    /api/orders/customers/{customer_id} # List customer orders
POST   /api/orders/{order_id}/items     # Add line item
DELETE /api/orders/{order_id}/items/{item_id} # Remove line item
POST   /api/orders/{order_id}/submit    # Submit for payment
POST   /api/orders/{order_id}/payment   # Confirm payment
POST   /api/orders/{order_id}/ship      # Ship order
POST   /api/orders/{order_id}/cancel    # Cancel order
```

### Example API Usage

```bash
# Create a new order
curl -X POST http://localhost:8000/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "123e4567-e89b-12d3-a456-426614174000",
    "shipping_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94102",
      "country": "US"
    }
  }'

# Add a product to the order
curl -X POST http://localhost:8000/api/orders/{order_id}/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "223e4567-e89b-12d3-a456-426614174000",
    "quantity": 2,
    "unit_price": 29.99,
    "currency": "USD"
  }'

# Submit the order
curl -X POST http://localhost:8000/api/orders/{order_id}/submit
```

### Running Tests

```bash
# Unit tests only (fast, no database)
pytest tests/unit/ -v

# Integration tests (requires PostgreSQL running)
pytest tests/integration/ -v

# Full suite with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Type checking
mypy src/

# Linting
ruff check src/
black --check src/
isort --check-only src/
```

### Development Workflow

```bash
# 1. Make changes to code

# 2. Run tests
pytest tests/unit/ -v

# 3. Type check
mypy src/

# 4. Format code
black src/
isort src/

# 5. Lint
ruff check src/ --fix

# 6. Commit
git add .
git commit -m "feat: add feature X"
```

### Docker Setup

```bash
# Start services (PostgreSQL + Redis)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset database (WARNING: deletes all data!)
docker-compose down -v
docker-compose up -d
```

## Implementation Status

### ✅ Completed
- **Domain Layer**: Order aggregate, value objects, domain events
- **Application Layer**: Commands, queries, DTOs, handlers
- **Infrastructure Layer**: PostgreSQL repository, SQLAlchemy models, event publisher
- **HTTP API**: FastAPI REST endpoints with full CRUD operations
- **Docker Setup**: Docker Compose for PostgreSQL and Redis
- **Documentation**: OpenAPI/Swagger UI at `/docs`

### 🚧 Future Enhancements

#### Phase 5: Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- API key management
- Rate limiting per user

#### Phase 6: Advanced Event-Driven Features
- Redis Streams event bus (replace in-memory)
- Event sourcing for complete audit trail
- Transactional outbox pattern
- Fulfillment service subscriber (stub)
- Idempotency for external API calls

#### Phase 7: Observability & Monitoring
- Structured logging with structlog
- Prometheus metrics endpoint
- Grafana dashboards
- Distributed tracing with OpenTelemetry
- Health checks with detailed status

#### Phase 8: Performance & Scalability
- Database query optimization
- Connection pooling tuning
- Caching layer (Redis)
- Read replicas for queries
- Horizontal scaling strategy

#### Phase 9: Testing & Quality
- Integration tests for API endpoints
- E2E tests with test fixtures
- Property-based testing (hypothesis)
- Performance/load testing (Locust)
- Contract testing for external APIs

#### Phase 10: Deployment & Operations
- Kubernetes manifests
- Helm charts
- CI/CD pipeline (GitHub Actions)
- Database migrations with Alembic
- Blue-green deployment
- Rollback strategy

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
