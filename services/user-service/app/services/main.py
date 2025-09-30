"""
User Service - FastAPI application for user authentication and management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import auth
from shared.config import get_app_config
from shared.exceptions import EduPlatformException

# Get configuration
app_config = get_app_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("Starting User Service...")
    yield
    # Shutdown
    print("Shutting down User Service...")


# Create FastAPI application
app = FastAPI(
    title="EduPlatform User Service",
    description="User authentication and management service",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.base.cors_origins,
    allow_credentials=True,
    allow_methods=app_config.base.cors_methods,
    allow_headers=app_config.base.cors_headers,
)


# Exception handler
@app.exception_handler(EduPlatformException)
async def eduplatform_exception_handler(request: Request, exc: EduPlatformException):
    """Handle custom EduPlatform exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "0.1.0",
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
