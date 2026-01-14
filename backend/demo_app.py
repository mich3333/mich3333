#!/usr/bin/env python3
"""
Demo version of the Order Management API using SQLite instead of PostgreSQL.

This allows running the API without Docker for demonstration purposes.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Import our modules
from src.interfaces.http.routes.orders import router as orders_router
from src.infrastructure.persistence.postgres.models import Base

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# SQLite async engine (in-memory for demo)
DATABASE_URL = "sqlite+aiosqlite:///./demo_orders.db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionFactory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Order Management API (Demo with SQLite)...")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("✅ API is ready!")
    logger.info("📖 Docs available at: http://localhost:8000/docs")

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await engine.dispose()
    logger.info("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="Order Management API (Demo)",
    description="RESTful API for managing orders using Domain-Driven Design - SQLite Demo Version",
    version="1.0.0-demo",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(orders_router)


# Health check
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "order-management-api",
        "database": "SQLite (demo)",
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "service": "Order Management API (Demo)",
        "version": "1.0.0-demo",
        "database": "SQLite",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "note": "Using SQLite for demo. For production, use PostgreSQL with Docker Compose.",
    }


# Dependency injection - override session factory
async def get_db_session():
    """Get database session for dependency injection"""
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override the dependency in routes
from src.infrastructure.persistence.postgres import get_db_session as original_get_db_session
app.dependency_overrides[original_get_db_session] = get_db_session


if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🎉 Order Management API - Demo Version")
    print("=" * 70)
    print()
    print("📦 Using SQLite database (demo_orders.db)")
    print("🌐 Starting server at http://localhost:8000")
    print("📖 API Docs at http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    uvicorn.run(
        "demo_app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
