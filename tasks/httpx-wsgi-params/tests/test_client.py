import json


def echo_app(environ, start_response):
    if environ["PATH_INFO"] == "/missing":
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [b'{"error": "not found"}']
    body = {"path": environ["PATH_INFO"], "query": environ.get("QUERY_STRING", ""), "token": environ.get("HTTP_X_TOKEN")}
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps(body).encode()]


from app.client import get_json, make_client, search_url


def test_get_json_with_token():
    client = make_client(echo_app, token="abc")
    assert get_json(client, "/status") == {"path": "/status", "query": "", "token": "abc"}


def test_search_url():
    assert search_url(make_client(echo_app), "red shoes") == "http://service/search?q=red%20shoes&page=1"
