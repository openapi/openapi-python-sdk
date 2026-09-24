import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from openapi_python_sdk.client import AsyncClient, AsyncOauthClient


class TestAsyncRetry(unittest.IsolatedAsyncioTestCase):

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_default_no_retries(self, mock_sleep, mock_httpx):
        """Verify that max_retries defaults to 0 and does not retry on network error."""
        # Setup mock to raise a request error
        mock_httpx.return_value.request = AsyncMock(side_effect=httpx.RequestError("Network error"))
        mock_httpx.return_value.aclose = AsyncMock()

        async with AsyncClient(token="test_token") as client:
            self.assertEqual(client.max_retries, 0)
            with self.assertRaises(httpx.RequestError):
                await client.request(method="GET", url="https://test.example.com")

        # Request should only be called once
        self.assertEqual(mock_httpx.return_value.request.call_count, 1)
        mock_sleep.assert_not_called()

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_successful_request_no_retries(self, mock_sleep, mock_httpx):
        """Verify that a successful request is only called once even if max_retries > 0."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_httpx.return_value.request = AsyncMock(return_value=mock_resp)
        mock_httpx.return_value.aclose = AsyncMock()

        async with AsyncClient(token="test_token", max_retries=3, backoff_factor=0.001) as client:
            resp = await client.request(method="GET", url="https://test.example.com")

        self.assertEqual(resp, {"status": "ok"})
        self.assertEqual(mock_httpx.return_value.request.call_count, 1)
        mock_sleep.assert_not_called()

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_retry_on_network_error_then_success(self, mock_sleep, mock_httpx):
        """Verify client retries on network error and succeeds on subsequent try."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_httpx.return_value.aclose = AsyncMock()

        # First two requests fail, third succeeds
        mock_httpx.return_value.request = AsyncMock(side_effect=[
            httpx.RequestError("Error 1"),
            httpx.RequestError("Error 2"),
            mock_resp,
        ])

        async with AsyncClient(token="test_token", max_retries=3, backoff_factor=0.1) as client:
            resp = await client.request(method="GET", url="https://test.example.com")

        self.assertEqual(resp, {"status": "ok"})
        self.assertEqual(mock_httpx.return_value.request.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_retry_limit_reached(self, mock_sleep, mock_httpx):
        """Verify that client fails after reaching max_retries limit."""
        mock_httpx.return_value.request = AsyncMock(side_effect=httpx.RequestError("Error"))
        mock_httpx.return_value.aclose = AsyncMock()

        async with AsyncClient(token="test_token", max_retries=2, backoff_factor=0.1) as client:
            with self.assertRaises(httpx.RequestError):
                await client.request(method="GET", url="https://test.example.com")

        # Initial call + 2 retries = 3 calls
        self.assertEqual(mock_httpx.return_value.request.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_retry_on_status_codes(self, mock_sleep, mock_httpx):
        """Verify client retries on configured retry status codes (e.g. 503)."""
        mock_resp_fail = MagicMock()
        mock_resp_fail.status_code = 503

        mock_resp_success = MagicMock()
        mock_resp_success.status_code = 200
        mock_resp_success.json.return_value = {"status": "ok"}
        mock_httpx.return_value.aclose = AsyncMock()

        mock_httpx.return_value.request = AsyncMock(side_effect=[
            mock_resp_fail,
            mock_resp_success,
        ])

        async with AsyncClient(token="test_token", max_retries=3, backoff_factor=0.1) as client:
            resp = await client.request(method="GET", url="https://test.example.com")

        self.assertEqual(resp, {"status": "ok"})
        self.assertEqual(mock_httpx.return_value.request.call_count, 2)
        mock_sleep.assert_called_once()

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_respects_retry_after_header(self, mock_sleep, mock_httpx):
        """Verify client respects Retry-After header on 429 Too Many Requests."""
        mock_resp_429 = MagicMock()
        mock_resp_429.status_code = 429
        mock_resp_429.headers = {"Retry-After": "5"}

        mock_resp_success = MagicMock()
        mock_resp_success.status_code = 200
        mock_resp_success.json.return_value = {"status": "ok"}
        mock_httpx.return_value.aclose = AsyncMock()

        mock_httpx.return_value.request = AsyncMock(side_effect=[
            mock_resp_429,
            mock_resp_success,
        ])

        async with AsyncClient(token="test_token", max_retries=3, backoff_factor=1.0) as client:
            resp = await client.request(method="GET", url="https://test.example.com")

        self.assertEqual(resp, {"status": "ok"})
        # Should sleep for exactly 5.0 seconds as specified by Retry-After
        mock_sleep.assert_called_once_with(5.0)

    @patch("openapi_python_sdk.client.httpx.AsyncClient")
    @patch("asyncio.sleep")
    async def test_oauth_client_retry(self, mock_sleep, mock_httpx):
        """Verify that AsyncOauthClient also supports retries."""
        mock_resp_fail = MagicMock()
        mock_resp_fail.status_code = 502

        mock_resp_success = MagicMock()
        mock_resp_success.status_code = 200
        mock_resp_success.json.return_value = {"token": "abc123"}
        mock_httpx.return_value.aclose = AsyncMock()

        mock_httpx.return_value.post = AsyncMock(side_effect=[
            mock_resp_fail,
            mock_resp_success,
        ])

        async with AsyncOauthClient(username="user", apikey="key", max_retries=2, backoff_factor=0.1) as oauth:
            resp = await oauth.create_token(scopes=["test"])

        self.assertEqual(resp["token"], "abc123")
        self.assertEqual(mock_httpx.return_value.post.call_count, 2)
        mock_sleep.assert_called_once()


if __name__ == "__main__":
    unittest.main()
