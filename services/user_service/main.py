"""
User Service - Manages users and authentication.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import config
from shared.exceptions.auth import (
    AccountDisabledError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from shared.exceptions.base import AlreadyExistsError, NotFoundError, ValidationError
from shared.messaging.kafka_producer import get_kafka_producer

from .app.routes import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("Starting User Service...")

    # Start Kafka producer (optional for development)
    kafka_producer = None
    try:
        kafka_producer = await get_kafka_producer()
        await kafka_producer.start()
    except Exception as e:
        print(f"⚠️  Kafka unavailable: {e}")
        print("⚠️  Running without event publishing")

    yield

    # Stop Kafka producer
    if kafka_producer:
        try:
            await kafka_producer.stop()
        except:
            pass
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

    # Exception handlers
    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request, exc: InvalidCredentialsError
    ):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AccountDisabledError)
    async def account_disabled_handler(request: Request, exc: AccountDisabledError):
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
        )

    @app.exception_handler(InvalidTokenError)
    async def invalid_token_handler(request: Request, exc: InvalidTokenError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
        )

    @app.exception_handler(AlreadyExistsError)
    async def already_exists_handler(request: Request, exc: AlreadyExistsError):
        return JSONResponse(
            status_code=409,
            content={"detail": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
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
