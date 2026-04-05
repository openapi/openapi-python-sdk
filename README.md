<div align="center">
  <a href="https://openapi.com/">
    <img alt="Openapi SDK for Python" src=".github/assets/repo-header-a3.png" >
  </a>

  <h1>Openapi® client for Python</h1>
  <h4>The perfect starting point to integrate <a href="https://openapi.com/">Openapi®</a> within your Python project</h4>

[![Build](https://github.com/openapi/openapi-python-sdk/actions/workflows/python.yml/badge.svg)](https://github.com/openapi/openapi-python-sdk/actions/workflows/python.yml)
[![PyPI Version](https://img.shields.io/pypi/v/openapi-python-sdk)](https://pypi.org/project/openapi-python-sdk/)
[![Python Versions](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://pypi.org/project/openapi-python-sdk/)
[![License](https://img.shields.io/github/license/openapi/openapi-python-sdk)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/openapi-python-sdk)](https://pypi.org/project/openapi-python-sdk/)
<br>
[![Linux Foundation Member](https://img.shields.io/badge/Linux%20Foundation-Silver%20Member-003778?logo=linux-foundation&logoColor=white)](https://www.linuxfoundation.org/about/members)
</div>

## Overview

A minimal and agnostic Python SDK for Openapi, inspired by a clean client implementation. This SDK provides only the core HTTP primitives needed to interact with any Openapi service.

## Pre-requisites

Before using the Openapi Python Client, you will need an account at [Openapi](https://console.openapi.com/) and an API key to the sandbox and/or production environment

## Features

- **Agnostic Design**: No API-specific classes, works with any OpenAPI service
- **Minimal Dependencies**: Only requires Python 3.8+ and `httpx`
- **OAuth Support**: Built-in OAuth client for token management
- **HTTP Primitives**: GET, POST, PUT, DELETE, PATCH methods
- **Async Support**: Fully compatible with async frameworks like FastAPI and aiohttp
- **Clean Interface**: Similar to the Rust SDK design

## What you can do

With the Openapi Python Client, you can easily interact with a variety of services in the Openapi Marketplace. For example, you can:

- 📩 **Send SMS messages** with delivery reports and custom sender IDs
- 💸 **Process bills and payments** in real time via API
- 🧾 **Send electronic invoices** securely to the Italian Revenue Agency
- 📄 **Generate PDFs** from HTML content, including JavaScript rendering
- ✉️ **Manage certified emails** and legal communications via Italian Legalmail

For a complete list of all available services, check out the [Openapi Marketplace](https://console.openapi.com/) 🌐


## Installation

The package is available on [PyPI](https://pypi.org/project/openapi-python-sdk/) and supports Python 3.10 and above.
Install it with pip:

```bash
pip install openapi-python-sdk
```

If you are using Poetry:

```bash
poetry add openapi-python-sdk
```

No additional configuration is needed. The only runtime dependency is [`httpx`](https://www.python-httpx.org/).

## Usage

Interaction with the Openapi platform happens in two distinct steps.

### Step 1 — Generate a token

Authenticate with your credentials and obtain a short-lived bearer token scoped to the endpoints you need.

```python
from openapi_python_sdk import OauthClient

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

Use the token to make authenticated requests to any Openapi service.

```python
from openapi_python_sdk import Client

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

### Customizing the Transport Layer

If you need to configure custom retry logic, proxies, or use a different HTTP client (such as passing a `requests.Session` with a custom urllib3 `Retry`), you can inject it directly using the `client` parameter on any SDK class:

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from openapi_python_sdk import Client
import requests

retry = Retry(total=3)
adapter = HTTPAdapter(max_retries=retry)

session = requests.Session()
session.mount("https://", adapter)

# Pass the custom session to the Client explicitly
client = Client("token", client=session)
```

## Async Usage

The SDK provides `AsyncClient` and `AsyncOauthClient` for use with asynchronous frameworks like FastAPI or `aiohttp`.

### Async Authentication

```python
from openapi_python_sdk import AsyncOauthClient

async with AsyncOauthClient(username="<your_username>", apikey="<your_apikey>", test=True) as oauth:
    resp = await oauth.create_token(
        scopes=["GET:test.imprese.openapi.it/advance"],
        ttl=3600,
    )
    token = resp["token"]
```

### Async Requests

```python
from openapi_python_sdk import AsyncClient

async with AsyncClient(token=token) as client:
    resp = await client.request(
        method="GET",
        url="https://test.imprese.openapi.it/advance",
        params={"denominazione": "altravia"},
    )
```


## Testing

Install dev dependencies and run the test suite:

```bash
pip install pytest
pytest
```

Or with Poetry:

```bash
poetry install
poetry run pytest
```




## Contributing

Contributions are always welcome! Whether you want to report bugs, suggest new features, improve documentation, or contribute code, your help is appreciated.

See [docs/contributing.md](docs/contributing.md) for detailed instructions on how to get started. Please make sure to follow this project's [docs/code-of-conduct.md](docs/code-of-conduct.md) to help maintain a welcoming and collaborative environment.

## Authors

Meet the project authors:

- Michael Cuffaro ([@maiku1008](https://www.github.com/maiku1008))
- Openapi Team ([@openapi-it](https://github.com/openapi-it))

## Partners

Meet our partners using Openapi or contributing to this SDK:

- [Blank](https://www.blank.app/)
- [Credit Safe](https://www.creditsafe.com/)
- [Deliveroo](https://deliveroo.it/)
- [Gruppo MOL](https://molgroupitaly.it/it/)
- [Jakala](https://www.jakala.com/)
- [Octotelematics](https://www.octotelematics.com/)
- [OTOQI](https://otoqi.com/)
- [PWC](https://www.pwc.com/)
- [QOMODO S.R.L.](https://www.qomodo.me/)
- [SOUNDREEF S.P.A.](https://www.soundreef.com/)

## Our Commitments

We believe in open source and we act on that belief. We became Silver Members
of the Linux Foundation because we wanted to formally support the ecosystem
we build on every day. Open standards, open collaboration, and open governance
are part of how we work and how we think about software.

## License

This project is licensed under the [MIT License](LICENSE).

The MIT License is a permissive open-source license that allows you to freely use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, provided that the original copyright notice and this permission notice are included in all copies or substantial portions of the software.

In short, you are free to use this SDK in your personal, academic, or commercial projects, with minimal restrictions. The project is provided "as-is", without any warranty of any kind, either expressed or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.

For more details, see the full license text at the [MIT License page](https://choosealicense.com/licenses/mit/).
