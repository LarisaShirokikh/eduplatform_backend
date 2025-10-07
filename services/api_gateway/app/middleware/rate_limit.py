"""
Simple in-memory rate limiting middleware.
"""

import time
from collections import defaultdict
from typing import Dict

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware using in-memory storage."""

    def __init__(self, app, requests_per_minute: int = 10):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        print(f"Rate limiting initialized: {requests_per_minute} requests/minute")

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""

        # Get client IP
        client_ip = request.client.host
        print(f"Request from {client_ip}, path: {request.url.path}")

        # Current time
        now = time.time()

        # Clean old requests (older than 1 minute)
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] if now - req_time < 60
        ]

        # Count current requests
        request_count = len(self.requests[client_ip])
        print(
            f"Client {client_ip} has made {request_count} requests in the last minute"
        )

        # Check rate limit
        if request_count >= self.requests_per_minute:
            print(f"RATE LIMIT EXCEEDED for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute}/minute",
                },
            )

        # Add current request
        self.requests[client_ip].append(now)

        # Process request
        response = await call_next(request)
        return response
