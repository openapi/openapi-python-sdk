"""
Step 1 — Token Generation
=========================
Authenticate with your credentials and create a short-lived bearer token
scoped to the API endpoints you need to call.

Usage:
    OPENAPI_USERNAME=<user> OPENAPI_APIKEY=<key> python examples/token_generation.py
"""

import os

from openapi_python_sdk.client import OauthClient

username = os.environ.get("OPENAPI_USERNAME", "<your_username>")
apikey = os.environ.get("OPENAPI_APIKEY", "<your_apikey>")

oauth = OauthClient(username=username, apikey=apikey, test=True)

# Create a token valid for 1 hour, scoped to the endpoints you need
resp = oauth.create_token(
    scopes=[
        "GET:test.imprese.openapi.it/advance",
        "POST:test.postontarget.com/fields/country",
    ],
    ttl=3600,
)
token = resp["token"]
print(f"Token created: {token}")

# Revoke the token when you are done
oauth.delete_token(id=token)
print("Token revoked.")
