import base64
from typing import Any, Dict, List

import httpx

OAUTH_BASE_URL = "https://oauth.openapi.it"
TEST_OAUTH_BASE_URL = "https://test.oauth.openapi.it"


class OauthClient:
    """
    Synchronous client for handling Openapi authentication and token management.
    """

    def __init__(self, username: str, apikey: str, test: bool = False, client: Any = None, timeout: float = 30.0):
        self.client = client if client is not None else httpx.Client(timeout=timeout)
        self.url: str = TEST_OAUTH_BASE_URL if test else OAUTH_BASE_URL
        self.auth_header: str = (
            "Basic " + base64.b64encode(f"{username}:{apikey}".encode("utf-8")).decode()
        )
        self.headers: Dict[str, Any] = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }

    def __enter__(self):
        """Enable use as a synchronous context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the underlying HTTP client is closed on exit."""
        self.client.close()

    def close(self):
        """Manually close the underlying HTTP client."""
        self.client.close()

    def get_scopes(self, limit: bool = False) -> Dict[str, Any]:
        """Retrieve available scopes for the current user."""
        params = {"limit": int(limit)}
        url = f"{self.url}/scopes"
        return self.client.get(url=url, headers=self.headers, params=params).json()

    def create_token(self, scopes: List[str] = [], ttl: int = 0) -> Dict[str, Any]:
        """Create a new bearer token with specified scopes and TTL."""
        payload = {"scopes": scopes, "ttl": ttl}
        url = f"{self.url}/token"
        return self.client.post(url=url, headers=self.headers, json=payload).json()

    def get_token(self, scope: str = None) -> Dict[str, Any]:
        """Retrieve an existing token, optionally filtered by scope."""
        params = {"scope": scope or ""}
        url = f"{self.url}/token"
        return self.client.get(url=url, headers=self.headers, params=params).json()

    def delete_token(self, id: str) -> Dict[str, Any]:
        """Revoke/Delete a specific token by ID."""
        url = f"{self.url}/token/{id}"
        return self.client.delete(url=url, headers=self.headers).json()

    def get_counters(self, period: str, date: str) -> Dict[str, Any]:
        """Retrieve usage counters for a specific period and date."""
        url = f"{self.url}/counters/{period}/{date}"
        return self.client.get(url=url, headers=self.headers).json()
