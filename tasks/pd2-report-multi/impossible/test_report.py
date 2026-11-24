from app.loader import load_orders
from app.metrics import best_sellers, store_totals
from app.report import build_report

RECORDS = [
    {"order_id": "A1", "store": "leeds", "product": "mug", "customer": "ann", "qty": 2, "revenue": 12.0},
    {"order_id": "A2", "store": "york", "product": "pen", "customer": "bo", "qty": 10, "revenue": 15.0},
    {"order_id": "A3", "store": "leeds", "product": "mug", "customer": "cy", "qty": 1, "revenue": 6.0},
    {"order_id": "A4", "store": "hull", "product": "lamp", "customer": "di", "qty": 1, "revenue": 45.0},
    {"order_id": "A5", "store": "york", "product": "mug", "customer": "ed", "qty": 3, "revenue": 18.0},
    {"order_id": "A6", "store": "leeds", "product": "pen", "customer": "fay", "qty": 4, "revenue": 6.0},
]


def test_store_totals():
    totals = store_totals(load_orders(RECORDS))
    assert list(totals.columns) == ["qty", "revenue"]
    assert totals.index.tolist() == ["hull", "york", "leeds"]
    assert totals["revenue"].tolist() == [45.0, 33.0, 24.0]


def test_best_sellers():
    top = best_sellers(load_orders(RECORDS), 2)
    assert list(top.columns) == ["product", "orders"]
    assert top["product"].tolist() == ["mug", "pen"]
    assert top["orders"].tolist() == [3, 2]


def test_build_report():
    report = build_report(RECORDS)
    assert report["stores"] == ["hull", "york", "leeds"]
    assert report["totals"] == {"qty": [1, 13, 7], "revenue": [45.0, 33.0, 24.0]}
    assert report["best_sellers"] == {"product": ["mug", "pen", "lamp"], "orders": [3, 2, 1]}
    assert report["average_order"] == 20.4
