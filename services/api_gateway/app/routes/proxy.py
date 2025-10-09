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
RATE_LIMIT = 100  # requests per minute


def check_rate_limit(client_ip: str, limit: int = RATE_LIMIT) -> bool:
    """Check if client exceeded rate limit."""
    now = time.time()
    rate_limit_storage[client_ip] = [
        req_time for req_time in rate_limit_storage[client_ip] if now - req_time < 60
    ]

    if len(rate_limit_storage[client_ip]) >= limit:
        return True

    rate_limit_storage[client_ip].append(now)
    return False


async def proxy_request(request: Request, target_url: str, path: str) -> Response:
    """Proxy request to target service."""

    # Check rate limit
    client_ip = request.client.host
    if check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later.",
            },
        )

    url = f"{target_url}{path}"
    query_params = dict(request.query_params)
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        body = await request.body()
        response = await http_client.request(
            method=request.method,
            url=url,
            params=query_params,
            headers=headers,
            content=body,
        )

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


# Универсальный роут для всех сервисов
@router.api_route(
    "/api/v1/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    tags=["Proxy"],
)
async def universal_proxy(request: Request, service: str, path: str = ""):
    """
    Universal proxy for all microservices.

    Routes requests based on service name:
    - /api/v1/auth/* -> User Service
    - /api/v1/users/* -> User Service
    - /api/v1/courses/* -> Course Service
    """
    # Map service names to URLs
    service_map = {
        "auth": gateway_config.user_service_url,
        "users": gateway_config.user_service_url,
        "courses": gateway_config.course_service_url,
        "lessons": gateway_config.course_service_url,
        "progress": gateway_config.progress_service_url,
        "notifications": gateway_config.notification_service_url,
    }

    target_url = service_map.get(service)

    if not target_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service}' not found",
        )

    # Reconstruct full path
    full_path = f"/api/v1/{service}"
    if path:
        full_path = f"{full_path}/{path}"

    return await proxy_request(request, target_url, full_path)
