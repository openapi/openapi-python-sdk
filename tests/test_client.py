import unittest
from unittest.mock import MagicMock, patch

from openapi_python_sdk.client import Client, OauthClient


class TestOauthClient(unittest.TestCase):

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_create_token(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"token": "abc123"}
        mock_httpx.return_value.post.return_value = mock_resp

        oauth = OauthClient(username="user", apikey="key", test=True)
        resp = oauth.create_token(scopes=["GET:test.example.com/api"], ttl=3600)

        self.assertEqual(resp["token"], "abc123")
        mock_httpx.return_value.post.assert_called_once()

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_delete_token(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"success": True}
        mock_httpx.return_value.delete.return_value = mock_resp

        oauth = OauthClient(username="user", apikey="key", test=True)
        resp = oauth.delete_token(id="abc123")

        self.assertTrue(resp["success"])
        mock_httpx.return_value.delete.assert_called_once()

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_get_scopes(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"scopes": ["GET:test.example.com/api"]}
        mock_httpx.return_value.get.return_value = mock_resp

        oauth = OauthClient(username="user", apikey="key")
        resp = oauth.get_scopes()

        self.assertIn("scopes", resp)

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_uses_sandbox_url_when_test_true(self, mock_httpx):
        oauth = OauthClient(username="user", apikey="key", test=True)
        self.assertIn("test.", oauth.url)

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_uses_production_url_by_default(self, mock_httpx):
        oauth = OauthClient(username="user", apikey="key")
        self.assertNotIn("test.", oauth.url)

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_auth_header_is_basic(self, mock_httpx):
        oauth = OauthClient(username="user", apikey="key")
        self.assertTrue(oauth.auth_header.startswith("Basic "))


class TestClient(unittest.TestCase):

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_request_get(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"data": []}
        mock_httpx.return_value.request.return_value = mock_resp

        client = Client(token="abc123")
        resp = client.request(
            method="GET",
            url="https://test.imprese.openapi.it/advance",
            params={"denominazione": "altravia"},
        )

        self.assertEqual(resp, {"data": []})
        mock_httpx.return_value.request.assert_called_once()

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_request_post(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"result": "ok"}
        mock_httpx.return_value.request.return_value = mock_resp

        client = Client(token="abc123")
        resp = client.request(
            method="POST",
            url="https://test.postontarget.com/fields/country",
            payload={"limit": 0, "query": {"country_code": "IT"}},
        )

        self.assertEqual(resp["result"], "ok")

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_auth_header(self, mock_httpx):
        client = Client(token="mytoken")
        self.assertEqual(client.auth_header, "Bearer mytoken")
        self.assertEqual(client.headers["Authorization"], "Bearer mytoken")

    @patch("openapi_python_sdk.client.httpx.Client")
    def test_defaults_on_empty_request(self, mock_httpx):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_httpx.return_value.request.return_value = mock_resp

        client = Client(token="tok")
        resp = client.request()

        mock_httpx.return_value.request.assert_called_once_with(
            method="GET", url="", headers=client.headers, json={}, params={}
        )


if __name__ == "__main__":
    unittest.main()
