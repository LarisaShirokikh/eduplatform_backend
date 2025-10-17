"""
HTTP client for inter-service communication.
"""

from typing import Any, Optional

import httpx


class HTTPClient:
    """HTTP client for making requests to other services."""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize HTTP client.

        Args:
            base_url: Base URL of the service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def get(
        self,
        path: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make GET request.

        Args:
            path: Request path
            params: Query parameters
            headers: Request headers

        Returns:
            dict: Response JSON

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{path}"
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post(
        self,
        path: str,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make POST request.

        Args:
            path: Request path
            json: Request body as JSON
            headers: Request headers

        Returns:
            dict: Response JSON

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{path}"
        response = await self.client.post(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def put(
        self,
        path: str,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make PUT request.

        Args:
            path: Request path
            json: Request body as JSON
            headers: Request headers

        Returns:
            dict: Response JSON

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{path}"
        response = await self.client.put(url, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def delete(
        self,
        path: str,
        headers: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Make DELETE request.

        Args:
            path: Request path
            headers: Request headers

        Returns:
            dict: Response JSON

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = f"{self.base_url}{path}"
        response = await self.client.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
