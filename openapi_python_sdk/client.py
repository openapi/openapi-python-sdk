import json
import random
import threading
import time
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

    def __init__(
        self,
        token: str,
        client: Any = None,
        timeout: float = 30.0,
        max_retries: int = 0,
        backoff_factor: float = 1.0,
        retry_on_status: list[int] = None,
    ):
        self._client = client
        self._thread_local = threading.local()
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.retry_on_status = (
            retry_on_status if retry_on_status is not None else [429, 502, 503, 504]
        )
        self.auth_header: str = f"Bearer {token}"
        self.headers: Dict[str, str] = {
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

        if params:
            import urllib.parse
            query_string = urllib.parse.urlencode(params, doseq=True)
            url = f"{url}&{query_string}" if "?" in url else f"{url}?{query_string}"
            params = None

        resp = self._request_with_retry(
            self.client.request,
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
