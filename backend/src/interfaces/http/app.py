"""
FastAPI application setup.

Main entry point for the HTTP API.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes.orders import router as orders_router
from ...infrastructure.persistence.postgres import Database, set_db_instance


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


# Database instance (will be initialized on startup)
db: Database | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Order Management API...")

    # Initialize database
    global db
    database_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/orders"
    db = Database(database_url, echo=True)  # Set echo=False in production

    # Set global database instance for dependency injection
    set_db_instance(db)

    # Create tables (in production, use Alembic migrations instead)
    logger.info("📊 Creating database tables...")
    await db.create_tables()

    logger.info("✅ API is ready!")

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    if db:
        await db.close()
    logger.info("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="Order Management API",
    description="RESTful API for managing orders using Domain-Driven Design",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(orders_router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "order-management-api"}


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Order Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
        log_level="info",
    )
