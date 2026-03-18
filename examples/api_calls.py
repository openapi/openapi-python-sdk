"""
Step 2 — API Calls
==================
Use a previously generated bearer token to call Openapi endpoints.
Run token_generation.py first, then paste the token below (or pass it via env).

Usage:
    OPENAPI_TOKEN=<token> python examples/api_calls.py
"""

import os

from openapi_python_sdk.client import Client

token = os.environ.get("OPENAPI_TOKEN", "<your_token>")

client = Client(token=token)

# GET request with query params
resp = client.request(
    method="GET",
    url="https://test.imprese.openapi.it/advance",
    params={"denominazione": "altravia", "provincia": "RM", "codice_ateco": "6201"},
)
print("GET response:", resp)

# POST request with a JSON payload
resp = client.request(
    method="POST",
    url="https://test.postontarget.com/fields/country",
    payload={"limit": 0, "query": {"country_code": "IT"}},
)
print("POST response:", resp)
