"""
Notification Service - Handles notifications and event processing.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from shared.messaging.kafka_consumer import KafkaConsumerManager

from .app.handlers.user_events import UserEventHandler

# Global consumer
consumer: KafkaConsumerManager = None
consumer_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global consumer, consumer_task

    print("🚀 Starting Notification Service...")

    # Initialize consumer
    consumer = KafkaConsumerManager(group_id="notification-service")
    await consumer.start()

    # Initialize event handler
    user_handler = UserEventHandler()

    # Start consuming in background
    consumer_task = asyncio.create_task(
        consumer.consume(
            topics=["user.registered", "user.login"],
            handler=user_handler.route_event,
        )
    )

    print("✅ Notification Service started and listening for events")

    yield

    # Cleanup
    print("🛑 Stopping Notification Service...")
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass

    if consumer:
        await consumer.stop()

    print("❌ Notification Service stopped")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="Notification Service API",
        description="Notification and event processing service for EduPlatform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "notification-service",
                "version": "0.1.0",
            }
        )

    return app


app = create_app()
