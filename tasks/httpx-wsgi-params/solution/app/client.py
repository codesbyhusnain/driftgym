from urllib.parse import quote

import httpx

BASE_URL = "http://service"


def make_client(app, token=None):
    headers = {"X-Token": token} if token else {}
    return httpx.Client(transport=httpx.WSGITransport(app=app), base_url=BASE_URL, headers=headers)


def search_url(client, query, page=1):
    query_string = f"q={quote(str(query), safe='')}&page={page}"
    return str(client.build_request("GET", f"/search?{query_string}").url)


def get_json(client, path):
    response = client.get(path)
    response.raise_for_status()
    return response.json()
