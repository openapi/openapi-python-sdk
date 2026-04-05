import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from openapi_python_sdk.client import AsyncClient, AsyncOauthClient


class TestAsyncOauthClient(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for AsyncOauthClient using IsolatedAsyncioTestCase
    which allows for native await calls in test methods.
    """

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    async def test_create_token(self, mock_httpx):
        # Mocking the response and the post method
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"token": "abc123"}
        mock_httpx.return_value.post = AsyncMock(return_value=mock_resp)
        mock_httpx.return_value.aclose = AsyncMock()

        # Testing the async context manager (__aenter__ / __aexit__)
        async with AsyncOauthClient(username="user", apikey="key", test=True) as oauth:
            resp = await oauth.create_token(scopes=["GET:test.example.com/api"], ttl=3600)

        self.assertEqual(resp["token"], "abc123")
        mock_httpx.return_value.post.assert_called_once()
        # Verify aclose was called by the context manager
        mock_httpx.return_value.aclose.assert_called_once()

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    async def test_get_scopes(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"scopes": ["GET:test.example.com/api"]}
        mock_httpx.return_value.get = AsyncMock(return_value=mock_resp)
        mock_httpx.return_value.aclose = AsyncMock()

        oauth = AsyncOauthClient(username="user", apikey="key")
        resp = await oauth.get_scopes()

        self.assertIn("scopes", resp)
        # Manually closing the client as we didn't use the context manager here
        await oauth.aclose()
        mock_httpx.return_value.aclose.assert_called_once()

    def test_custom_client_transport(self):
        custom_client = MagicMock()
        oauth = AsyncOauthClient(username="user", apikey="key", client=custom_client)
        self.assertEqual(oauth.client, custom_client)


class TestAsyncClient(unittest.IsolatedAsyncioTestCase):
    """
    Test suite for the generic AsyncClient.
    """

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    async def test_request_get(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": []}
        mock_httpx.return_value.request = AsyncMock(return_value=mock_resp)
        mock_httpx.return_value.aclose = AsyncMock()

        async with AsyncClient(token="abc123") as client:
            resp = await client.request(
                method="GET",
                url="https://test.imprese.openapi.it/advance",
                params={"denominazione": "altravia"},
            )

        self.assertEqual(resp, {"data": []})
        mock_httpx.return_value.request.assert_called_once()
        mock_httpx.return_value.aclose.assert_called_once()

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    async def test_request_post(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"result": "ok"}
        mock_httpx.return_value.request = AsyncMock(return_value=mock_resp)
        mock_httpx.return_value.aclose = AsyncMock()

        client = AsyncClient(token="abc123")
        resp = await client.request(
            method="POST",
            url="https://test.postontarget.com/fields/country",
            payload={"limit": 0, "query": {"country_code": "IT"}},
        )

        self.assertEqual(resp["result"], "ok")
        # Ensure cleanup
        await client.aclose()
        mock_httpx.return_value.aclose.assert_called_once()

    def test_custom_client_transport(self):
        custom_client = MagicMock()
        client = AsyncClient(token="abc123", client=custom_client)
        self.assertEqual(client.client, custom_client)


if __name__ == "__main__":
    unittest.main()
