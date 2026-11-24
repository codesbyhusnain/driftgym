import httpx

BASE_URL = "http://service"


def make_client(app, token=None):
    headers = {"X-Token": token} if token else {}
    return httpx.Client(app=app, base_url=BASE_URL, headers=headers)


def search_url(client, query, page=1):
    return str(client.build_request("GET", "/search", params={"q": query, "page": page}).url)


def get_json(client, path):
    response = client.get(path)
    response.raise_for_status()
    return response.json()
