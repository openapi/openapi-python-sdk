import base64
from typing import Any, Dict, List

import httpx

from .oauth_client import OAUTH_BASE_URL, TEST_OAUTH_BASE_URL


class AsyncOauthClient:
    """
    Asynchronous client for handling Openapi authentication and token management.
    Suitable for use with FastAPI, aiohttp, etc.
    """

    def __init__(self, username: str, apikey: str, test: bool = False, client: Any = None):
        self.client = client if client is not None else httpx.AsyncClient()
        self.url: str = TEST_OAUTH_BASE_URL if test else OAUTH_BASE_URL
        self.auth_header: str = (
            "Basic " + base64.b64encode(f"{username}:{apikey}".encode("utf-8")).decode()
        )
        self.headers: Dict[str, Any] = {
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

    async def get_scopes(self, limit: bool = False) -> Dict[str, Any]:
        """Retrieve available scopes for the current user (async)."""
        params = {"limit": int(limit)}
        url = f"{self.url}/scopes"
        resp = await self.client.get(url=url, headers=self.headers, params=params)
        return resp.json()

    async def create_token(self, scopes: List[str] = [], ttl: int = 0) -> Dict[str, Any]:
        """Create a new bearer token with specified scopes and TTL (async)."""
        payload = {"scopes": scopes, "ttl": ttl}
        url = f"{self.url}/token"
        resp = await self.client.post(url=url, headers=self.headers, json=payload)
        return resp.json()

    async def get_token(self, scope: str = None) -> Dict[str, Any]:
        """Retrieve an existing token, optionally filtered by scope (async)."""
        params = {"scope": scope or ""}
        url = f"{self.url}/token"
        resp = await self.client.get(url=url, headers=self.headers, params=params)
        return resp.json()

    async def delete_token(self, id: str) -> Dict[str, Any]:
        """Revoke/Delete a specific token by ID (async)."""
        url = f"{self.url}/token/{id}"
        resp = await self.client.delete(url=url, headers=self.headers)
        return resp.json()

    async def get_counters(self, period: str, date: str) -> Dict[str, Any]:
        """Retrieve usage counters for a specific period and date (async)."""
        url = f"{self.url}/counters/{period}/{date}"
        resp = await self.client.get(url=url, headers=self.headers)
        return resp.json()
