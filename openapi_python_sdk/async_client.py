import json
from typing import Any, Dict

import httpx


class AsyncClient:
    """
    Asynchronous client for making authenticated requests to Openapi endpoints.
    Suitable for use with FastAPI, aiohttp, etc.
    """

    def __init__(self, token: str):
        self.client = httpx.AsyncClient()
        self.auth_header: str = f"Bearer {token}"
        self.headers: Dict[str, str] = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }

    async def __aenter__(self):
        """Enable use as an asynchronous context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensure the underlying HTTP client is closed on exit (async)."""
        await self.client.aclose()

    async def aclose(self):
        """Manually close the underlying HTTP client (async)."""
        await self.client.aclose()

    async def request(
        self,
        method: str = "GET",
        url: str = None,
        payload: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Make an asynchronous HTTP request to the specified Openapi endpoint.
        """
        payload = payload or {}
        params = params or {}
        url = url or ""
        resp = await self.client.request(
            method=method,
            url=url,
            headers=self.headers,
            json=payload,
            params=params,
        )
        data = resp.json()

        # Handle cases where the API might return a JSON-encoded string instead of an object
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass

        return data
