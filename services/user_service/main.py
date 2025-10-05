"""
User Service - FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.config import get_app_config
from shared.exceptions import EduPlatformException

from .app.routes import auth, users

app_config = get_app_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting User Service...")
    yield
    print("Shutting down User Service...")


app = FastAPI(
    title="EduPlatform User Service",
    description="User authentication and management",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_config.base.cors_origins_list,
    allow_credentials=True,
    allow_methods=app_config.base.cors_methods_list,
    allow_headers=["*"],
)


@app.exception_handler(EduPlatformException)
async def eduplatform_exception_handler(request: Request, exc: EduPlatformException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "0.1.0",
    }


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
