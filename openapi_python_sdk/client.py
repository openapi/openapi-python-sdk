import base64
from typing import Any, Dict

import httpx

import json

OAUTH_BASE_URL = "https://oauth.openapi.it"
TEST_OAUTH_BASE_URL = "https://test.oauth.openapi.it"


class OauthClient:
    def __init__(self, username: str, apikey: str, test: bool = False):
        self.client = httpx.Client()
        self.url: str = TEST_OAUTH_BASE_URL if test else OAUTH_BASE_URL
        self.auth_header: str = (
            "Basic " + base64.b64encode(f"{username}:{apikey}".encode("utf-8")).decode()
        )
        self.headers: Dict[str, Any] = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }

    def get_scopes(self, limit: bool = False) -> Dict[str, Any]:
        params = {"limit": int(limit)}
        url = f"{self.url}/scopes"
        return self.client.get(url=url, headers=self.headers, params=params).json()

    def create_token(self, scopes: list[str] = [], ttl: int = 0) -> Dict[str, Any]:
        payload = {"scopes": scopes, "ttl": ttl}
        url = f"{self.url}/token"
        return self.client.post(url=url, headers=self.headers, json=payload).json()

    def get_token(self, scope: str = None) -> Dict[str, Any]:
        params = {"scope": scope or ""}
        url = f"{self.url}/token"
        return self.client.get(url=url, headers=self.headers, params=params).json()

    def delete_token(self, id: str) -> Dict[str, Any]:
        url = f"{self.url}/token/{id}"
        return self.client.delete(url=url, headers=self.headers).json()

    def get_counters(self, period: str, date: str) -> Dict[str, Any]:
        url = f"{self.url}/counters/{period}/{date}"
        return self.client.get(url=url, headers=self.headers).json()


class Client:
    def __init__(self, token: str):
        self.client = httpx.Client()
        self.auth_header: str = f"Bearer {token}"
        self.headers: Dict[str, str] = {
            "Authorization": self.auth_header,
            "Content-Type": "application/json",
        }

    def request(
        self,
        method: str = "GET",
        url: str = None,
        payload: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
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

        if isinstance(data,str):
            try:
                data=json.loads(data)
            except json.JSONDecodeError:
                pass
        return data