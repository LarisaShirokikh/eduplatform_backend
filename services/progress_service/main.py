"""
Progress Service - Tracks learning progress and course completion.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import config
from shared.messaging.kafka_producer import get_kafka_producer

from .app.routes import progress


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("🚀 Starting Progress Service...")

    # Start Kafka producer (optional for development)
    kafka_producer = None
    try:
        kafka_producer = await get_kafka_producer()
        await kafka_producer.start()
        print("✅ Kafka producer started")
    except Exception as e:
        print(f"⚠️  Kafka unavailable: {e}")
        print("⚠️  Running without event publishing")

    yield  # Только один yield!

    # Stop Kafka producer
    if kafka_producer:
        try:
            await kafka_producer.stop()
        except:
            pass
    print("🛑 Shutting down Progress Service...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Progress Service API",
        description="Learning progress tracking service for EduPlatform",
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
    app.include_router(progress.router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "progress-service",
                "version": "0.1.0",
            }
        )

    return app


app = create_app()
