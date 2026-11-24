import json

from app.web import create_app


def test_single_item_and_missing_item():
    client = create_app().test_client()
    response = client.get("/items/C3")
    assert response.get_data(as_text=True).strip() == '{"sku":"C3","name":"Cable","price":"3.25","since":"2024-02-29"}'
    missing = client.get("/items/ZZ")
    assert missing.status_code == 404
    assert json.loads(missing.get_data(as_text=True)) == {"error": "not found"}


def test_default_name_and_quotes():
    client = create_app().test_client()
    assert client.get("/hello").get_data(as_text=True) == "<p>Hello, world!</p>"
    body = client.get("/hello", query_string={"name": 'O"Neil & co'}).get_data(as_text=True)
    assert body == "<p>Hello, O&#34;Neil &amp; co!</p>"


def test_every_request_sees_the_catalogue():
    client = create_app().test_client()
    first = json.loads(client.get("/items").get_data(as_text=True))
    second = json.loads(client.get("/items").get_data(as_text=True))
    assert first == second
    assert [item["sku"] for item in first] == ["B2", "A1", "C3"]
    assert [item["price"] for item in first] == ["0.50", "12.00", "3.25"]
