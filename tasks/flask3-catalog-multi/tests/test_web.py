from app.web import create_app

ITEMS = (
    '[{"sku":"B2","name":"Bolt","price":"0.50","since":"2023-04-01"},'
    '{"sku":"A1","name":"Anchor","price":"12.00","since":"2021-11-30"},'
    '{"sku":"C3","name":"Cable","price":"3.25","since":"2024-02-29"}]'
)


def test_items_in_catalogue_order_with_keys_in_order():
    response = create_app().test_client().get("/items")
    assert response.status_code == 200
    assert response.get_data(as_text=True).strip() == ITEMS


def test_hello_escapes_the_name():
    response = create_app().test_client().get("/hello", query_string={"name": "<b>Ann</b>"})
    assert response.get_data(as_text=True) == "<p>Hello, &lt;b&gt;Ann&lt;/b&gt;!</p>"
