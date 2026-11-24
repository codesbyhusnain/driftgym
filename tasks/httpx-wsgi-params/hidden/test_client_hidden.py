import json


def echo_app(environ, start_response):
    if environ["PATH_INFO"] == "/missing":
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [b'{"error": "not found"}']
    body = {"path": environ["PATH_INFO"], "query": environ.get("QUERY_STRING", ""), "token": environ.get("HTTP_X_TOKEN")}
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps(body).encode()]


import httpx
import pytest

from app.client import get_json, make_client, search_url


def test_reserved_and_unicode_characters():
    client = make_client(echo_app)
    assert search_url(client, "fish & chips", 3) == "http://service/search?q=fish%20%26%20chips&page=3"
    assert search_url(client, "café 50%") == "http://service/search?q=caf%C3%A9%2050%25&page=1"
    assert search_url(client, "c++/x=y") == "http://service/search?q=c%2B%2B%2Fx%3Dy&page=1"


def test_search_url_reaches_the_app_unchanged():
    client = make_client(echo_app)
    body = get_json(client, search_url(client, "a b", 2))
    assert body == {"path": "/search", "query": "q=a%20b&page=2", "token": None}


def test_error_status_raises():
    with pytest.raises(httpx.HTTPStatusError):
        get_json(make_client(echo_app, token="t"), "/missing")
