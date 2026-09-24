import base64
import random
import threading
import time
from typing import Any, Dict, List

import httpx

OAUTH_BASE_URL = "https://oauth.openapi.it"
TEST_OAUTH_BASE_URL = "https://test.oauth.openapi.it"


class OauthClient:
    """
    Synchronous client for handling Openapi authentication and token management.
    """

    def __init__(
        self,
        username: str,
        apikey: str,
        test: bool = False,
        client: Any = None,
        timeout: float = 30.0,
        max_retries: int = 0,
        backoff_factor: float = 1.0,
        retry_on_status: List[int] = None,
    ):
        self._client = client
        self._thread_local = threading.local()
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_status = (
            retry_on_status if retry_on_status is not None else [429, 502, 503, 504]
        )
        self.url: str = TEST_OAUTH_BASE_URL if test else OAUTH_BASE_URL
        self.auth_header: str = (
            "Basic " + base64.b64encode(f"{username}:{apikey}".encode("utf-8")).decode()
        )
        self.headers: Dict[str, Any] = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }

    @property
    def client(self) -> Any:
        """
        Thread-safe access to the underlying HTTP client.
        If a custom client was provided at initialization, it is returned.
        Otherwise, a thread-local httpx.Client is created and returned.
        """
        if self._client is not None:
            return self._client
        if not hasattr(self._thread_local, "client"):
            self._thread_local.client = httpx.Client(timeout=self.timeout)
        return self._thread_local.client

    @client.setter
    def client(self, value: Any):
        self._client = value

    def __enter__(self):
        """Enable use as a synchronous context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure the underlying HTTP client is closed on exit."""
        self.client.close()

    def close(self):
        """Manually close the underlying HTTP client."""
        self.client.close()

    def _request_with_retry(self, request_fn, *args, **kwargs) -> httpx.Response:
        attempts = 0
        while True:
            try:
                resp = request_fn(*args, **kwargs)
                if resp.status_code in self.retry_on_status and attempts < self.max_retries:
                    attempts += 1
                    sleep_time = self.backoff_factor * (2 ** attempts) + random.uniform(0, 0.5)
                    if resp.status_code == 429:
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after:
                            try:
                                sleep_time = float(retry_after)
                            except ValueError:
                                pass
                    time.sleep(sleep_time)
                    continue
                return resp
            except httpx.RequestError as exc:
                if attempts < self.max_retries:
                    attempts += 1
                    sleep_time = self.backoff_factor * (2 ** attempts) + random.uniform(0, 0.5)
                    time.sleep(sleep_time)
                    continue
                raise exc

    def get_scopes(self, limit: bool = False) -> Dict[str, Any]:
        """Retrieve available scopes for the current user."""
        params = {"limit": int(limit)}
        url = f"{self.url}/scopes"
        resp = self._request_with_retry(self.client.get, url=url, headers=self.headers, params=params)
        return resp.json()

    def create_token(self, scopes: List[str] = [], ttl: int = 0) -> Dict[str, Any]:
        """Create a new bearer token with specified scopes and TTL."""
        payload = {"scopes": scopes, "ttl": ttl}
        url = f"{self.url}/token"
        resp = self._request_with_retry(self.client.post, url=url, headers=self.headers, json=payload)
        return resp.json()

    def get_token(self, scope: str = None) -> Dict[str, Any]:
        """Retrieve an existing token, optionally filtered by scope."""
        params = {"scope": scope or ""}
        url = f"{self.url}/token"
        resp = self._request_with_retry(self.client.get, url=url, headers=self.headers, params=params)
        return resp.json()

    def delete_token(self, id: str) -> Dict[str, Any]:
        """Revoke/Delete a specific token by ID."""
        url = f"{self.url}/token/{id}"
        resp = self._request_with_retry(self.client.delete, url=url, headers=self.headers)
        return resp.json()

    def get_counters(self, period: str, date: str) -> Dict[str, Any]:
        """Retrieve usage counters for a specific period and date."""
        url = f"{self.url}/counters/{period}/{date}"
        resp = self._request_with_retry(self.client.get, url=url, headers=self.headers)
        return resp.json()
