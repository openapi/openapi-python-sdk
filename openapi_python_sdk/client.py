import json
from typing import Any, Dict

import httpx

# Backward compatibility imports
from .async_client import AsyncClient  # noqa: F401
from .async_oauth_client import AsyncOauthClient  # noqa: F401
from .oauth_client import OauthClient  # noqa: F401


class Client:
    """
    Synchronous client for making authenticated requests to Openapi endpoints.
    """

    def __init__(self, token: str, client: Any = None):
        self.client = client if client is not None else httpx.Client()
        self.auth_header: str = f"Bearer {token}"
        self.headers: Dict[str, str] = {
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

    def request(
        self,
        method: str = "GET",
        url: str = None,
        payload: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Make a synchronous HTTP request to the specified Openapi endpoint.
        """
        payload = payload or {}
        params = params or {}
        url = url or ""
        data = self.client.request(
            method=method,
            url=url,
            headers=self.headers,
            json=payload,
            params=params,
        ).json()

        # Handle cases where the API might return a JSON-encoded string instead of an object
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass
        return data
