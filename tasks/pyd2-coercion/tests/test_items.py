from app.items import item_labels, order_total


ROWS = [
    {"sku": 1042, "quantity": 3, "unit_price": 2.5},
    {"sku": "B-7", "quantity": 2.9, "unit_price": "10", "note": 15},
]


def test_item_labels():
    assert item_labels(ROWS) == ["1042 x3", "B-7 x2"]


def test_order_total():
    assert order_total(ROWS) == 27.5
