"""
User Service - Manages users and authentication.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import config
from shared.messaging.kafka_producer import get_kafka_producer

from .app.routes import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("Starting User Service...")

    # Start Kafka producer
    kafka_producer = await get_kafka_producer()
    await kafka_producer.start()

    yield

    # Stop Kafka producer
    await kafka_producer.stop()
    print("Shutting down User Service...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="User Service API",
        description="User management and authentication service for EduPlatform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "user-service",
                "version": "0.1.0",
            }
        )

    return app


app = create_app()
