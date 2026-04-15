# openapi-python-sdk

A minimal Python SDK for [Openapi®](https://openapi.it) — the largest certified API marketplace in Italy.
Provides the core HTTP primitives to authenticate and interact with any Openapi service, without API-specific coupling.

## Requirements

- Python 3.10+
- An account on [console.openapi.com](https://console.openapi.com/) with a valid API key

## Installation

```bash
pip install openapi-python-sdk
```

## Usage

Interaction with the Openapi platform happens in two distinct steps.

### Step 1 — Generate a token

```python
from openapi_python_sdk.client import OauthClient

oauth = OauthClient(username="<your_username>", apikey="<your_apikey>", test=True)

resp = oauth.create_token(
    scopes=[
        "GET:test.imprese.openapi.it/advance",
        "POST:test.postontarget.com/fields/country",
    ],
    ttl=3600,
)
token = resp["token"]

# Revoke the token when done
oauth.delete_token(id=token)
```

### Step 2 — Call an API endpoint

```python
from openapi_python_sdk.client import Client

client = Client(token=token)

# GET with query params
resp = client.request(
    method="GET",
    url="https://test.imprese.openapi.it/advance",
    params={"denominazione": "altravia", "provincia": "RM", "codice_ateco": "6201"},
)

# POST with a JSON payload
resp = client.request(
    method="POST",
    url="https://test.postontarget.com/fields/country",
    payload={"limit": 0, "query": {"country_code": "IT"}},
)
```

### Configuring Network Timeouts

By default, the SDK uses a 30-second timeout for all network requests. You can easily override it passing a `timeout` explicitly during initialization:

```python
from openapi_python_sdk.client import Client

client = Client(token="token", timeout=60.0) # 60 seconds
```

## Testing

```bash
pip install pytest
pytest
```

## OauthClient API

| Method | Description |
|---|---|
| `OauthClient(username, apikey, test=False, timeout=30.0)` | Initialize the OAuth client. Set `test=True` for sandbox. |
| `create_token(scopes, ttl)` | Create a bearer token for the given scopes and TTL (seconds). |
| `get_token(scope)` | Retrieve an existing token by scope. |
| `delete_token(id)` | Revoke a token by ID. |
| `get_scopes(limit=False)` | List available scopes. |
| `get_counters(period, date)` | Retrieve usage counters for a given period and date. |

## Client API

| Method | Description |
|---|---|
| `Client(token, timeout=30.0)` | Initialize the client with a bearer token. |
| `request(method, url, payload, params)` | Execute an HTTP request against any Openapi endpoint. |

## Links

- Homepage: [openapi.it](https://openapi.it)
- Console & API keys: [console.openapi.com](https://console.openapi.com/)
- GitHub: [github.com/openapi/openapi-python-sdk](https://github.com/openapi/openapi-python-sdk)
- Issue tracker: [github.com/openapi/openapi-python-sdk/issues](https://github.com/openapi/openapi-python-sdk/issues)

## License

MIT — see [LICENSE](https://github.com/openapi/openapi-python-sdk/blob/main/LICENSE) for details.

## Authors

- Michael Cuffaro ([@maiku1008](https://github.com/maiku1008))
- Openapi Team ([@openapi-it](https://github.com/openapi-it))
