"""
SQLAlchemy ORM models for PostgreSQL persistence.

These models map domain aggregates to database tables.
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Column,
    String,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class OrderModel(Base):
    """
    ORM model for Order aggregate.

    Maps to 'orders' table in PostgreSQL.
    """

    __tablename__ = "orders"

    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)

    # Business identifiers
    customer_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)

    # Status
    status = Column(String(50), nullable=False, index=True)

    # Money
    total_amount = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total_currency = Column(String(3), nullable=False, default="USD")

    # Addresses (embedded as columns)
    shipping_street = Column(String(255), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(50), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(2), nullable=False)

    billing_street = Column(String(255), nullable=False)
    billing_city = Column(String(100), nullable=False)
    billing_state = Column(String(50), nullable=False)
    billing_postal_code = Column(String(20), nullable=False)
    billing_country = Column(String(2), nullable=False)

    # Tracking & timestamps
    tracking_number = Column(String(100), nullable=True)
    payment_id = Column(PostgresUUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    payment_confirmed_at = Column(DateTime, nullable=True)
    processing_started_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Optimistic locking
    version = Column(Integer, nullable=False, default=0)

    # Relationships
    line_items = relationship(
        "LineItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="joined",  # Eager load line items with order
    )

    # Indexes
    __table_args__ = (
        Index("idx_orders_customer_status", "customer_id", "status"),
        Index("idx_orders_created_at", "created_at"),
        CheckConstraint("total_amount >= 0", name="check_positive_total"),
    )

    def __repr__(self):
        return f"<OrderModel(id={self.id}, status={self.status}, total={self.total_amount})>"


class LineItemModel(Base):
    """
    ORM model for LineItem entity.

    Maps to 'line_items' table in PostgreSQL.
    """

    __tablename__ = "line_items"

    # Primary key
    id = Column(PostgresUUID(as_uuid=True), primary_key=True)

    # Foreign key to order
    order_id = Column(PostgresUUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True)

    # Product reference
    product_id = Column(PostgresUUID(as_uuid=True), nullable=False)

    # Quantity
    quantity = Column(Integer, nullable=False)

    # Unit price (Money value object)
    unit_price_amount = Column(Numeric(10, 2), nullable=False)
    unit_price_currency = Column(String(3), nullable=False, default="USD")

    # Relationship
    order = relationship("OrderModel", back_populates="line_items")

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_positive_quantity"),
        CheckConstraint("unit_price_amount >= 0", name="check_positive_price"),
    )

    def __repr__(self):
        return f"<LineItemModel(id={self.id}, product={self.product_id}, qty={self.quantity})>"


class DomainEventModel(Base):
    """
    ORM model for storing domain events (Event Sourcing / Audit Trail).

    Maps to 'domain_events' table in PostgreSQL.
    """

    __tablename__ = "domain_events"

    # Primary key (sequence)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Event metadata
    event_id = Column(PostgresUUID(as_uuid=True), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    aggregate_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    aggregate_type = Column(String(50), nullable=False, default="Order")

    # Event payload (JSON)
    event_data = Column(String, nullable=False)  # JSON serialized

    # Timestamps
    occurred_at = Column(DateTime, nullable=False, index=True)
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Indexing for queries
    __table_args__ = (
        Index("idx_events_aggregate", "aggregate_id", "occurred_at"),
        Index("idx_events_type_time", "event_type", "occurred_at"),
    )

    def __repr__(self):
        return f"<DomainEventModel(id={self.id}, type={self.event_type}, aggregate={self.aggregate_id})>"
