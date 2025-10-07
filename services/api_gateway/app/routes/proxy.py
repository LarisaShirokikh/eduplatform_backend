"""
Proxy routes for forwarding requests to microservices.
"""

import time
from collections import defaultdict

import httpx
from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from ..config import gateway_config

router = APIRouter()

# HTTP client для проксирования запросов
http_client = httpx.AsyncClient(timeout=30.0)

# In-memory rate limiting storage
rate_limit_storage = defaultdict(list)
RATE_LIMIT = 10  # requests per minute


def check_rate_limit(client_ip: str, limit: int = RATE_LIMIT) -> bool:
    """
    Check if client exceeded rate limit.

    Returns:
        bool: True if limit exceeded
    """
    now = time.time()

    # Clean old requests
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip] if now - req_time < 60
    ]

    request_count = len(rate_limit_storage[client_ip])
    print(f"DEBUG: Client {client_ip} has {request_count} requests, limit is {limit}")

    # Check limit
    if request_count >= limit:
        print(f"DEBUG: RATE LIMIT EXCEEDED for {client_ip}")
        return True

    # Add current request
    rate_limit_storage[client_ip].append(now)
    print(
        f"DEBUG: Added request for {client_ip}, now has {len(rate_limit_storage[client_ip])} requests"
    )
    return False


async def proxy_request(request: Request, target_url: str, path: str) -> Response:
    """Proxy request to target service."""
    print(f"DEBUG: proxy_request called for {path}")
    # Check rate limit
    client_ip = request.client.host
    print(f"DEBUG: Checking rate limit for {client_ip}")
    if check_rate_limit(client_ip):
        print(f"DEBUG: Rate limit exceeded, raising 429")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
            },
        )
    print(f"DEBUG: Rate limit OK, proxying request")
    # Построить полный URL
    url = f"{target_url}{path}"

    # Получить query параметры
    query_params = dict(request.query_params)

    # Получить заголовки (исключая host)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        # Получить тело запроса
        body = await request.body()

        # Проксировать запрос
        response = await http_client.request(
            method=request.method,
            url=url,
            params=query_params,
            headers=headers,
            content=body,
        )

        # Вернуть ответ
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except httpx.TimeoutException:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "Service timeout"},
        )
    except httpx.RequestError as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"Service unavailable: {str(e)}"},
        )


# Auth routes
@router.post("/api/v1/auth/register", tags=["User Service - Auth"])
async def proxy_auth_register(request: Request):
    """Proxy register to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/auth/register"
    )


@router.post("/api/v1/auth/login", tags=["User Service - Auth"])
async def proxy_auth_login(request: Request):
    """Proxy login to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/auth/login"
    )


@router.post("/api/v1/auth/refresh", tags=["User Service - Auth"])
async def proxy_auth_refresh(request: Request):
    """Proxy refresh token to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/auth/refresh"
    )


@router.post("/api/v1/auth/verify-email", tags=["User Service - Auth"])
async def proxy_auth_verify(request: Request):
    """Proxy email verification to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/auth/verify-email"
    )


# User routes
@router.get("/api/v1/users/me", tags=["User Service - Users"])
async def proxy_get_me(request: Request):
    """Proxy get current user to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/users/me"
    )


@router.put("/api/v1/users/me", tags=["User Service - Users"])
async def proxy_update_me(request: Request):
    """Proxy update current user to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/users/me"
    )


@router.delete("/api/v1/users/me", tags=["User Service - Users"])
async def proxy_delete_me(request: Request):
    """Proxy delete current user to User Service."""
    return await proxy_request(
        request, gateway_config.user_service_url, "/api/v1/users/me"
    )
