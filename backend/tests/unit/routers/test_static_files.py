import os

import pytest
from ampf.testing import ApiTestClient


@pytest.fixture
def static_client(client: ApiTestClient) -> ApiTestClient:  # type: ignore
    os.makedirs("static/browser/en", exist_ok=True)
    with open("static/browser/en/index.html", "wt", encoding="utf-8") as f:
        f.write("Hello from index.html")
    with open("static/browser/en/app.css", "wt", encoding="utf-8") as f:
        f.write("Hello from app.css")

    yield client  # type: ignore
    os.remove("static/browser/en/index.html")
    os.remove("static/browser/en/app.css")


def test_get_index_html(static_client):
    # When: Browser require existing file
    response = static_client.get("/en/index.html")
    # Then: index.html is returned
    assert "text/html" in response.headers["content-type"]
    assert "Hello from index.html" in response.text
