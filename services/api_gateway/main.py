"""
API Gateway for EduPlatform.
Central entry point for all microservices.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from services.api_gateway.app.middleware.rate_limit import limiter
from services.api_gateway.app.routes import proxy
from shared.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("API Gateway starting...")
    yield
    print("API Gateway shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title="EduPlatform API Gateway",
        description="Central API Gateway for EduPlatform microservices",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include proxy routes
    app.include_router(proxy.router)
    print(f"Registered {len(proxy.router.routes)} proxy routes")  # Для отладки

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return JSONResponse(
            content={"status": "healthy", "service": "api-gateway", "version": "0.1.0"}
        )

    return app


app = create_app()
