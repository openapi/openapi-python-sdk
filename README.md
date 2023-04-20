
# OpenApi IT Python Client 

This client is used to interact with the API found at [openapi.it](https://openapi.it/)

## Pre-requisites

Before using the OpenApi IT Python Client, you will need an account at [openapi.it](https://openapi.it/) and an API key to the sandbox and/or production environment

## Installation

You can install the OpenApi IT Python Client with the following command using go get:

```bash
pip install openapi-cli-python
```
    
## Usage


```python
from openapi.client import Client, OauthClient

# Initialize the oauth client on the sandbox environment
oauth_client = OauthClient(
    username="<your_username>", apikey="<your_apikey>", test=True
)

# Create a token for a list of scopes
resp = oauth_client.create_token(
    scopes=[
        "GET:test.imprese.openapi.it/advance",
        "POST:test.postontarget.com/fields/country",
    ],
    ttl=3600,
)
token = resp["token"]

# Initialize the client
client = Client(token=token)

# Make a request with params
resp = client.request(
    method="GET",
    url="https://test.imprese.openapi.it/advance",
    params={"denominazione": "altravia", "provincia": "RM", "codice_ateco": "6201"},
)

# Make a request with a payload
resp = client.request(
    method="POST",
    url="https://test.postontarget.com/fields/country",
    payload={"limit": 0, "query": { "country_code": "IT"}}
)

# Delete the token
resp = oauth_client.delete_token(id=token)
```

## Contributing

Contributions are always welcome!

See `contributing.md` for ways to get started.

Please adhere to this project's `code of conduct`.


## License

[MIT](https://choosealicense.com/licenses/mit/)


## Authors

- [@maiku1008](https://www.github.com/maiku1008)
- [@openapi-it](https://github.com/openapi-it)
