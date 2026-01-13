# Architectural Review & Redesign

**Author:** Senior Backend Engineer
**Date:** 2026-01-13
**Project:** AI Agent System → Domain-Driven Backend System

---

## Executive Summary

The current codebase contains **two experimental AI agent systems** built as demos, not production software. This review proposes a **controlled reset** to transform the underlying ideas into a senior-level portfolio project using Domain-Driven Design, explicit boundaries, and industry-standard patterns.

**Recommendation:** Archive the existing agent systems and rebuild as a **modular monolith** with the Order Management domain as the foundation.

---

## Part 1: Analysis of Current Architecture

### 1.1 What Exists Today

```
mich3333/
├── autonomous-claude/          # Single-agent system with memory
│   ├── autonomous_agent.py     # Decision loop
│   ├── memory.py               # Dual-memory (SQLite + Qdrant)
│   ├── claude_brain.py         # AI integration
│   └── web_app.py              # Flask REST API
│
├── multi-agent-system/         # Multi-agent orchestration
│   ├── agents/                 # 6 specialized agents
│   ├── orchestrator.py         # Coordinator
│   ├── models/state.py         # Shared MissionContext
│   └── frontend/               # React SPA
│
└── main.py                     # Quick-start demo
```

### 1.2 Critical Problems

#### **Problem 1: No Domain Model**
- System is organized around **technical patterns** (agents, memory, orchestration)
- No business domain concepts (Order, Invoice, Customer, Product)
- All logic lives in "agents" that do everything
- **Impact:** Cannot reason about business rules or invariants

#### **Problem 2: Global Mutable State**
- `MissionContext` is a shared bag of data passed between agents
- No encapsulation, no boundaries
- Any agent can modify anything
- **Impact:** Impossible to guarantee correctness

#### **Problem 3: Memory as a Crutch**
- Long-term memory (Qdrant vector DB) used to store domain facts
- Semantic search replaces proper state management
- No schema, no validation, no referential integrity
- **Impact:** Data integrity is impossible to verify

#### **Problem 4: Agent-Centric Architecture**
- Every operation goes through an "agent" with an LLM call
- Business logic is hidden inside AI prompts
- Deterministic operations (calculate total, validate email) use GPT
- **Impact:** Slow, expensive, non-deterministic, untestable

#### **Problem 5: No Transactional Boundaries**
- Operations span multiple agents with no atomicity
- Partial failures leave system in inconsistent state
- No rollback, no saga pattern, no compensation
- **Impact:** Data corruption risk

#### **Problem 6: Anemic REST API**
- Endpoints expose technical operations (`/api/agent/start`, `/api/execute`)
- No resource-oriented API (no `/orders`, `/customers`)
- WebSocket used for operational logs, not domain events
- **Impact:** Cannot be used as a real backend

### 1.3 What Should Be Deleted

| Component | Reason | Action |
|-----------|--------|--------|
| `autonomous_agent.py` | Agent pattern not needed | **DELETE** |
| `decision_loop.py` | Not a domain concept | **DELETE** |
| `orchestrator.py` | Multi-agent coordination unnecessary | **DELETE** |
| `agents/manager.py` | Business logic hidden in prompts | **DELETE** |
| `agents/researcher.py` | Research not a domain | **DELETE** |
| `agents/coder.py` | Code generation not a domain | **DELETE** |
| `agents/reviewer.py` | Review not a domain | **DELETE** |
| `memory.py` (short-term) | Ring buffer not needed | **DELETE** |
| `models/state.py` | Anemic shared state | **DELETE** |

### 1.4 What Should Be Archived

| Component | Value | Destination |
|-----------|-------|-------------|
| Long-term memory (Qdrant) | Interesting ML experiment | `experiments/semantic-memory/` |
| Browser automation | Useful for scraping demo | `experiments/browser-automation/` |
| Figma integration | Cool showcase feature | `experiments/figma-importer/` |
| WebSocket streaming | Good for real-time updates | `experiments/realtime-streaming/` |

### 1.5 What Can Be Reimagined

| Current Component | Domain Concept |
|-------------------|----------------|
| `MissionContext.execution_plan` | **Order** (with line items, state machine) |
| `AgentLog` audit trail | **Domain Events** (OrderCreated, OrderShipped) |
| `shared_findings.research_data` | **Product Catalog** (domain repository) |
| `shared_findings.code_artifacts` | **Fulfillment Items** (trackable work units) |
| `ReviewDecision` feedback loop | **Approval Workflow** (domain service) |
| Manager task decomposition | **Order Planning** (bounded context) |

---

## Part 2: Proposed Architecture

### 2.1 Architectural Principles

1. **Domain-Driven Design (DDD)**
   - Explicit domain model with entities, value objects, aggregates
   - Ubiquitous language shared with business stakeholders
   - Bounded contexts for different subdomains

2. **Modular Monolith**
   - Single deployable unit
   - Strong module boundaries (no cross-module imports except via interfaces)
   - Can be split into microservices later if needed

3. **Hexagonal Architecture (Ports & Adapters)**
   - Domain layer has no dependencies
   - Application layer orchestrates use cases
   - Infrastructure adapters are swappable

4. **No Global State**
   - All state owned by aggregates
   - State transitions through domain methods
   - No shared mutable memory

5. **Explicit Invariants**
   - Business rules enforced at write time
   - Invalid states unrepresentable
   - Type system used for correctness

### 2.2 System Overview

**Project Type:** E-commerce Order Management System
**Primary Domain:** Order Lifecycle
**Supporting Domains:** Catalog, Billing, Fulfillment

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                      │
│  (HTTP API, CLI, Background Jobs)                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                            │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    Order     │  │   Catalog    │  │   Billing    │    │
│  │   (core)     │  │ (supporting) │  │ (supporting) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ Fulfillment  │  │   Customer   │                       │
│  │ (supporting) │  │ (supporting) │                       │
│  └──────────────┘  └──────────────┘                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│  (Postgres, Redis, S3, Email, Payment Gateway)             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Domain Selection Rationale

**Selected Core Domain: Order Management**

**Why Order?**
1. **Complexity:** State machines, workflows, invariants, concurrency
2. **Central:** Connects all other domains (catalog, billing, fulfillment)
3. **Demonstrable:** Easy to explain, widely understood business concept
4. **Rich Behavior:** Not just CRUD—business logic, policies, events
5. **Interview-Ready:** Common system design question

**What Makes It Senior-Level?**
- Proper aggregate design (Order + LineItems)
- State machine with valid transitions
- Consistency boundaries (what changes together)
- Domain events for decoupling
- Eventual consistency patterns
- Idempotency for external integrations

---

## Part 3: Order Management Domain Design

### 3.1 Domain Model

```python
# Core Aggregate
class Order:
    """
    Order aggregate root.

    Invariants:
    - Order total must match sum of line items
    - Cannot modify order after it's shipped
    - Cannot ship order until payment confirmed
    - Minimum order value enforced
    """
    id: OrderId                    # Value object
    customer_id: CustomerId
    status: OrderStatus            # State machine
    line_items: List[LineItem]     # Entities owned by Order
    billing_info: BillingInfo      # Value object
    shipping_address: Address      # Value object
    total: Money                   # Value object
    created_at: datetime
    updated_at: datetime
    version: int                   # Optimistic locking

    # Domain Events (raised, not stored in aggregate)
    _events: List[DomainEvent]

# Entity (part of Order aggregate)
class LineItem:
    id: LineItemId
    product_id: ProductId
    quantity: Quantity             # Value object (positive int)
    unit_price: Money

    def subtotal(self) -> Money:
        return self.unit_price * self.quantity

# Value Objects (immutable)
class OrderStatus(Enum):
    DRAFT = "draft"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Money:
    amount: Decimal
    currency: str  # ISO 4217

    def __add__(self, other: Money) -> Money:
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
```

### 3.2 State Machine

```
DRAFT ──(submit)──> PENDING_PAYMENT ──(confirm_payment)──> CONFIRMED
  │                                                            │
  │                                                            │
  └──────────────────(cancel)──────────────────────────┐     │
                                                        │     │
                                                        ▼     ▼
                                                    CANCELLED PROCESSING
                                                              │
                                                              │
                                                      (ship)  │
                                                              ▼
                                                          SHIPPED
                                                              │
                                                              │
                                                    (deliver) │
                                                              ▼
                                                         DELIVERED
```

**Valid Transitions:**
- `DRAFT → PENDING_PAYMENT`: Submit order (validate items, calculate total)
- `PENDING_PAYMENT → CONFIRMED`: Payment confirmed by gateway
- `CONFIRMED → PROCESSING`: Fulfillment started
- `PROCESSING → SHIPPED`: Items shipped
- `SHIPPED → DELIVERED`: Customer confirmed delivery
- `DRAFT|PENDING_PAYMENT → CANCELLED`: Cancellation allowed before processing

**Invariants Enforced:**
1. Cannot add items after `PENDING_PAYMENT`
2. Cannot cancel after `PROCESSING`
3. Cannot modify shipping address after `CONFIRMED`

### 3.3 Domain Operations

```python
class Order:
    """Aggregate root with behavior"""

    def add_item(self, product: Product, quantity: int) -> None:
        """Add line item (only in DRAFT)"""
        if self.status != OrderStatus.DRAFT:
            raise OrderNotModifiableError(
                f"Cannot add items to order in {self.status} state"
            )

        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be positive")

        # Check if product already exists, update quantity
        existing = self._find_line_item(product.id)
        if existing:
            existing.quantity += quantity
        else:
            line_item = LineItem(
                id=LineItemId.generate(),
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price
            )
            self.line_items.append(line_item)

        self._recalculate_total()
        self._raise_event(LineItemAdded(order_id=self.id, ...))

    def submit(self) -> None:
        """Transition DRAFT → PENDING_PAYMENT"""
        if self.status != OrderStatus.DRAFT:
            raise InvalidStateTransitionError(...)

        if not self.line_items:
            raise EmptyOrderError("Cannot submit order with no items")

        if self.total < Money(Decimal("5.00"), "USD"):
            raise MinimumOrderValueError("Minimum order is $5")

        self.status = OrderStatus.PENDING_PAYMENT
        self._raise_event(OrderSubmitted(order_id=self.id, total=self.total))

    def confirm_payment(self, payment_id: PaymentId) -> None:
        """Transition PENDING_PAYMENT → CONFIRMED"""
        if self.status != OrderStatus.PENDING_PAYMENT:
            raise InvalidStateTransitionError(...)

        self.status = OrderStatus.CONFIRMED
        self._raise_event(
            PaymentConfirmed(order_id=self.id, payment_id=payment_id)
        )

    def cancel(self, reason: str) -> None:
        """Cancel order (only before PROCESSING)"""
        if self.status not in [OrderStatus.DRAFT, OrderStatus.PENDING_PAYMENT]:
            raise OrderNotCancellableError(
                f"Cannot cancel order in {self.status} state"
            )

        self.status = OrderStatus.CANCELLED
        self._raise_event(OrderCancelled(order_id=self.id, reason=reason))

    # ... ship(), deliver(), etc.

    def _recalculate_total(self) -> None:
        """Maintain invariant: total = sum(line_items)"""
        self.total = sum(
            item.subtotal() for item in self.line_items,
            start=Money(Decimal("0"), "USD")
        )
```

### 3.4 Repository Interface

```python
# Domain layer defines interface (port)
class OrderRepository(ABC):
    """Repository for Order aggregates"""

    @abstractmethod
    def next_id(self) -> OrderId:
        """Generate unique ID"""
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        """
        Persist aggregate.

        Raises:
            OptimisticLockError: If version mismatch (concurrent update)
        """
        pass

    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Load aggregate by ID"""
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: CustomerId) -> List[Order]:
        """Query by customer (read model)"""
        pass

# Infrastructure layer provides implementation
class PostgresOrderRepository(OrderRepository):
    """Concrete adapter"""

    def save(self, order: Order) -> None:
        # Transactional save with optimistic locking
        with self.db.transaction():
            # UPDATE orders SET ... WHERE id = ? AND version = ?
            # If no rows updated, raise OptimisticLockError
            # INSERT line_items ...
            # Increment version
            pass
```

### 3.5 Application Service (Use Case)

```python
class PlaceOrderService:
    """
    Application service coordinates use case.
    Does NOT contain business logic (that's in the domain).
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        payment_gateway: PaymentGateway,
        event_publisher: EventPublisher,
        unit_of_work: UnitOfWork
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_gateway = payment_gateway
        self.event_publisher = event_publisher
        self.uow = unit_of_work

    def execute(self, command: PlaceOrderCommand) -> OrderId:
        """
        Place a new order.

        Steps:
        1. Validate products exist
        2. Create Order aggregate
        3. Add line items (business logic in aggregate)
        4. Submit order (triggers state transition)
        5. Initiate payment (external integration)
        6. Publish domain events
        """
        with self.uow:
            # Fetch products (supporting domain)
            products = []
            for item in command.items:
                product = self.product_repo.find_by_id(item.product_id)
                if not product:
                    raise ProductNotFoundError(item.product_id)
                if not product.is_available():
                    raise ProductUnavailableError(item.product_id)
                products.append((product, item.quantity))

            # Create aggregate
            order_id = self.order_repo.next_id()
            order = Order.create(
                order_id=order_id,
                customer_id=command.customer_id,
                shipping_address=command.shipping_address,
                billing_info=command.billing_info
            )

            # Business logic (in aggregate)
            for product, quantity in products:
                order.add_item(product, quantity)

            order.submit()

            # Persist
            self.order_repo.save(order)

            # External integration (idempotent)
            payment_result = self.payment_gateway.initiate_payment(
                idempotency_key=str(order_id),
                amount=order.total,
                customer=command.customer_id
            )

            # Publish events (transactional outbox pattern)
            for event in order.collect_events():
                self.event_publisher.publish(event)

            self.uow.commit()

            return order_id
```

### 3.6 Domain Events

```python
# Events represent "something that happened" (past tense)
@dataclass(frozen=True)
class OrderSubmitted(DomainEvent):
    order_id: OrderId
    customer_id: CustomerId
    total: Money
    occurred_at: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class PaymentConfirmed(DomainEvent):
    order_id: OrderId
    payment_id: PaymentId
    occurred_at: datetime = field(default_factory=datetime.utcnow)

# Events consumed by other bounded contexts
class FulfillmentService:
    """Subscriber in Fulfillment bounded context"""

    @event_handler(PaymentConfirmed)
    def on_payment_confirmed(self, event: PaymentConfirmed) -> None:
        """
        When payment confirmed, start fulfillment process.
        This is eventual consistency—Fulfillment doesn't need to be
        synchronous with Order.
        """
        fulfillment_order = self.create_fulfillment_order(event.order_id)
        self.fulfillment_repo.save(fulfillment_order)
```

---

## Part 4: Implementation Structure

### 4.1 Folder Structure

```
backend/                           # New modular monolith
├── src/
│   ├── domain/                    # Pure business logic (no dependencies)
│   │   ├── order/                 # Order bounded context
│   │   │   ├── __init__.py
│   │   │   ├── aggregates/
│   │   │   │   ├── order.py              # Order aggregate root
│   │   │   │   └── line_item.py          # Entity
│   │   │   ├── value_objects/
│   │   │   │   ├── order_id.py
│   │   │   │   ├── order_status.py
│   │   │   │   ├── money.py
│   │   │   │   └── address.py
│   │   │   ├── events/
│   │   │   │   ├── order_submitted.py
│   │   │   │   ├── payment_confirmed.py
│   │   │   │   └── order_cancelled.py
│   │   │   ├── repositories/
│   │   │   │   └── order_repository.py   # Interface (ABC)
│   │   │   └── exceptions.py
│   │   │
│   │   ├── catalog/               # Catalog bounded context
│   │   │   ├── aggregates/
│   │   │   │   └── product.py
│   │   │   └── repositories/
│   │   │       └── product_repository.py
│   │   │
│   │   ├── billing/               # Billing bounded context
│   │   │   └── ...
│   │   │
│   │   └── shared/                # Shared kernel
│   │       ├── domain_event.py
│   │       └── entity.py
│   │
│   ├── application/               # Use cases / Application services
│   │   ├── commands/
│   │   │   ├── place_order.py            # PlaceOrderCommand + Handler
│   │   │   ├── cancel_order.py
│   │   │   └── confirm_payment.py
│   │   ├── queries/
│   │   │   ├── get_order.py
│   │   │   └── list_customer_orders.py
│   │   └── services/
│   │       └── order_service.py
│   │
│   ├── infrastructure/            # Adapters (depend on domain interfaces)
│   │   ├── persistence/
│   │   │   ├── postgres/
│   │   │   │   ├── postgres_order_repository.py
│   │   │   │   ├── postgres_product_repository.py
│   │   │   │   └── unit_of_work.py
│   │   │   └── migrations/       # Alembic
│   │   │       └── versions/
│   │   ├── messaging/
│   │   │   ├── event_publisher.py
│   │   │   └── redis_event_bus.py
│   │   ├── external/
│   │   │   ├── stripe_payment_gateway.py
│   │   │   └── sendgrid_email_service.py
│   │   └── config.py
│   │
│   ├── interfaces/                # Entry points (HTTP, CLI, etc.)
│   │   ├── http/
│   │   │   ├── app.py                    # Flask/FastAPI app factory
│   │   │   ├── routes/
│   │   │   │   ├── orders.py             # POST /orders, GET /orders/:id
│   │   │   │   ├── products.py
│   │   │   │   └── health.py
│   │   │   ├── serializers/
│   │   │   │   └── order_serializer.py   # DTO → JSON
│   │   │   └── middleware/
│   │   │       ├── auth.py
│   │   │       └── error_handler.py
│   │   └── cli/
│   │       └── commands.py               # CLI for admin tasks
│   │
│   └── main.py                    # Application entry point
│
├── tests/
│   ├── unit/                      # Domain logic tests (fast, no I/O)
│   │   ├── domain/
│   │   │   └── order/
│   │   │       ├── test_order_aggregate.py
│   │   │       └── test_state_machine.py
│   │   └── application/
│   │       └── test_place_order_service.py
│   ├── integration/               # Repository, external services
│   │   └── infrastructure/
│   │       └── test_postgres_order_repository.py
│   └── e2e/                       # End-to-end API tests
│       └── test_order_api.py
│
├── experiments/                   # Archived experimental code
│   ├── semantic-memory/           # Qdrant + embeddings
│   ├── browser-automation/        # Playwright demo
│   └── multi-agent-orchestration/ # Original agent system
│
├── docs/
│   ├── architecture/
│   │   ├── adr/                   # Architecture Decision Records
│   │   │   ├── 001-modular-monolith.md
│   │   │   ├── 002-ddd-order-aggregate.md
│   │   │   └── 003-event-driven-integration.md
│   │   ├── domain-model.md
│   │   └── api-design.md
│   └── setup.md
│
├── pyproject.toml                 # Dependencies (Poetry/uv)
├── Makefile                       # Common tasks (test, lint, migrate)
└── README.md                      # Portfolio README
```

### 4.2 Module Dependency Rules

```
interfaces → application → domain
     ↓           ↓
infrastructure ──┘

RULES:
1. Domain has ZERO dependencies (pure Python)
2. Application depends ONLY on domain interfaces
3. Infrastructure implements domain interfaces
4. Interfaces (HTTP/CLI) depend on application + infrastructure
5. NO circular dependencies between bounded contexts
```

### 4.3 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **HTTP API** | FastAPI | Async, type hints, OpenAPI, modern |
| **Database** | PostgreSQL | ACID, complex queries, mature |
| **Migrations** | Alembic | Industry standard for SQLAlchemy |
| **Event Bus** | Redis Streams | Lightweight, good enough for monolith |
| **Testing** | pytest + hypothesis | Property-based tests for invariants |
| **Validation** | Pydantic v2 | Type-safe DTOs, serialization |
| **ORM** | SQLAlchemy 2.0 | Explicit mapping, no magic |
| **Task Queue** | Celery + Redis | Background jobs (emails, webhooks) |
| **Monitoring** | Prometheus + Grafana | Metrics (order rate, p95 latency) |
| **Logging** | structlog | Structured JSON logs |

---

## Part 5: Architectural Decisions

### ADR-001: Why Modular Monolith?

**Context:** Need to demonstrate architectural thinking without over-engineering.

**Decision:** Build as modular monolith, not microservices.

**Rationale:**
1. **Senior engineers know when NOT to use microservices**
2. Monolith enforces stronger consistency guarantees
3. Easier to refactor when boundaries are wrong
4. Can extract to microservices later if needed
5. Demonstrates restraint and pragmatism

**Consequences:**
- All bounded contexts in same codebase
- Shared database (separate schemas per context)
- Faster development, simpler deployment

### ADR-002: Why Order Management First?

**Context:** Need one domain to showcase depth, not breadth.

**Decision:** Implement Order Management, stub others.

**Rationale:**
1. Orders connect all other domains (demonstrates integration thinking)
2. Rich state machine (not just CRUD)
3. Clear invariants to protect
4. Common interview question
5. Easy to explain to non-technical reviewers

**Consequences:**
- Catalog/Billing/Fulfillment are stubs initially
- Focus 80% effort on Order aggregate correctness
- Other domains added iteratively

### ADR-003: Why Domain Events?

**Context:** Need loose coupling between bounded contexts.

**Decision:** Use domain events for inter-context communication.

**Rationale:**
1. Decouples Order from Fulfillment/Billing
2. Enables eventual consistency
3. Event sourcing ready (future evolution)
4. Demonstrates async thinking

**Implementation:**
- Transactional outbox pattern (events in same DB transaction)
- Redis Streams for event bus (simple, reliable)
- Retry with exponential backoff

### ADR-004: Why No ORM Magic?

**Context:** Want to demonstrate understanding of persistence.

**Decision:** Use SQLAlchemy with explicit mapping, not Active Record.

**Rationale:**
1. **Data Mapper pattern separates domain from persistence**
2. Aggregate roots control their own consistency
3. No lazy loading surprises
4. Clear transaction boundaries

**Example:**
```python
# NO (Active Record - domain depends on DB)
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)

# YES (Data Mapper - domain is pure)
class Order:
    def __init__(self, id: OrderId, ...): ...

# Mapping defined separately
order_mapper = mapper(
    Order,
    orders_table,
    properties={'line_items': relationship(LineItem, ...)}
)
```

### ADR-005: Why No AI/LLM?

**Context:** Original system was AI-centric.

**Decision:** Remove all LLM calls from core domain.

**Rationale:**
1. **Deterministic business logic is better than AI guesses**
2. Calculate order total with arithmetic, not GPT
3. AI is appropriate for recommendations, not transactions
4. Demonstrates knowing when NOT to use AI

**Future Use Cases for AI:**
- Product recommendations (read-side, non-critical)
- Customer support chatbot (separate service)
- Fraud detection (ML model, not LLM)

---

## Part 6: Migration Path

### 6.1 What to Keep

| Component | Where It Goes |
|-----------|---------------|
| Flask API structure | → FastAPI in `interfaces/http/` |
| TypeScript frontend | → Keep as-is, update API calls |
| React frontend (multi-agent) | → Repurpose for order dashboard |
| Test infrastructure (pytest) | → Expand with domain tests |

### 6.2 Step-by-Step Migration

```
Phase 1: Foundation (Week 1)
├── Create new folder structure
├── Implement Order aggregate (domain)
├── Write comprehensive unit tests
├── Document domain model
└── No HTTP API yet (pure domain)

Phase 2: Application Layer (Week 2)
├── Implement PlaceOrderService
├── Add PostgreSQL repository
├── Add unit of work pattern
├── Integration tests with test DB
└── Still no HTTP API

Phase 3: API (Week 3)
├── FastAPI application
├── POST /orders, GET /orders/:id
├── Error handling middleware
├── OpenAPI documentation
└── E2E tests

Phase 4: Events & Integration (Week 4)
├── Event publisher (Redis)
├── Stub Fulfillment subscriber
├── Idempotency for external calls
└── Observability (logs, metrics)

Phase 5: Polish (Week 5)
├── Frontend integration
├── Docker Compose setup
├── README with architecture diagram
├── Record demo video
└── Deploy to portfolio site
```

### 6.3 Archival Process

```bash
# Archive experimental code
mkdir -p experiments/archived-$(date +%Y%m%d)

mv autonomous-claude experiments/semantic-memory
mv multi-agent-system experiments/multi-agent-orchestration

# Keep experiments folder in repo (shows evolution)
git add experiments/
git commit -m "Archive experimental agent systems"
```

---

## Part 7: Success Criteria

### For Portfolio Review

**What a senior engineer evaluates:**

✅ **Domain Model**
- [ ] Clear aggregate boundaries (Order owns LineItems)
- [ ] Invariants enforced (total = sum of items)
- [ ] State machine with valid transitions
- [ ] No anemic domain model

✅ **Architecture**
- [ ] Hexagonal architecture (ports & adapters)
- [ ] Domain layer has zero dependencies
- [ ] Proper separation of concerns
- [ ] No God objects or global state

✅ **Code Quality**
- [ ] Type hints everywhere (mypy strict mode)
- [ ] Comprehensive tests (unit, integration, E2E)
- [ ] No magic strings or numbers
- [ ] Defensive programming (validate inputs)

✅ **Pragmatism**
- [ ] Appropriate technology choices
- [ ] No over-engineering (no premature microservices)
- [ ] Clear ADRs explaining trade-offs
- [ ] Production-ready error handling

✅ **Communication**
- [ ] Clear README with architecture diagram
- [ ] API documentation (OpenAPI)
- [ ] Code comments where non-obvious
- [ ] Git history tells a story

### What NOT to Showcase

❌ **Anti-Patterns:**
- Complex agent orchestration (wrong abstraction)
- Global shared state (MissionContext)
- AI for deterministic operations
- Memory as database replacement
- Anemic REST API

---

## Part 8: Next Steps

### Immediate Actions

1. **Create new folder structure** (see Part 4.1)
2. **Implement Order aggregate** (see Part 3.3)
3. **Write unit tests for state machine**
4. **Document domain model with diagrams**
5. **Archive old agent systems**

### Questions to Answer

1. **Which payment gateway to integrate?** (Stripe vs. mock)
2. **Use FastAPI or Flask?** (Recommend FastAPI)
3. **Event sourcing from day 1?** (No, add later if needed)
4. **Include frontend in portfolio?** (Yes, but separate repo)

---

## Conclusion

The current experimental agent systems demonstrate interesting AI patterns but lack the architectural rigor expected in a senior portfolio. By resetting to a domain-driven approach with the Order Management domain as the foundation, this project will showcase:

1. **Deep domain modeling** (not just CRUD)
2. **Architectural decision-making** (modular monolith, DDD, hexagonal)
3. **Pragmatic technology choices** (Postgres, Redis, FastAPI)
4. **Professional engineering practices** (tests, types, docs)
5. **Communication skills** (ADRs, diagrams, clear code)

This is the difference between a "cool demo" and a "senior hire."

---

**Status:** Ready for implementation
**First Domain:** Order Management
**Next Review:** After Phase 1 completion
