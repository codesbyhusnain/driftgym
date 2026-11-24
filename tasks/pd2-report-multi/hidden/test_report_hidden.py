from app.loader import load_orders
from app.report import build_report


def _records():
    stores = ["bath", "kent", "bath", "derby", "kent", "bath", "derby", "bath"]
    products = ["tea", "tea", "jam", "tea", "jam", "scone", "tea", "tea"]
    qty = [1, 3, 2, 4, 1, 5, 2, 2]
    revenue = [5.0, 7.5, 3.0, 12.0, 4.0, 1.5, 6.0, 5.0]
    return [
        {"order_id": f"B{i}", "store": s, "product": p, "customer": f"c{i % 3}", "qty": q, "revenue": r}
        for i, (s, p, q, r) in enumerate(zip(stores, products, qty, revenue))
    ]


def test_load_orders_columns_types_and_index():
    orders = load_orders(_records())
    assert list(orders.columns) == ["order_id", "store", "product", "customer", "qty", "revenue"]
    assert list(orders.index) == list(range(8))
    assert orders["qty"].dtype == "int64"
    assert orders["revenue"].dtype == float


def test_report_on_other_orders():
    report = build_report(_records(), top=2)
    assert report["stores"] == ["derby", "bath", "kent"]
    assert report["totals"] == {"qty": [6, 10, 4], "revenue": [18.0, 14.5, 11.5]}
    assert report["best_sellers"] == {"product": ["tea", "jam"], "orders": [5, 2]}
    assert report["average_order"] == 5.5


def test_single_order():
    record = {"order_id": "Z9", "store": "ely", "product": "cake", "customer": "zed", "qty": 2, "revenue": 9.99}
    report = build_report([record])
    assert report["stores"] == ["ely"]
    assert report["totals"] == {"qty": [2], "revenue": [9.99]}
    assert report["best_sellers"] == {"product": ["cake"], "orders": [1]}
    assert report["average_order"] == 9.99


def test_no_orders():
    assert build_report([]) == {
        "stores": [],
        "totals": {"qty": [], "revenue": []},
        "best_sellers": {"product": [], "orders": []},
        "average_order": 0.0,
    }
