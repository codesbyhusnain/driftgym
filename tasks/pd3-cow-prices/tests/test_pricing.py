import pandas as pd

from app.pricing import apply_discounts, flag_low_stock

CATALOG = pd.DataFrame({"sku": ["A1", "B2", "C3"], "price": [20.0, 8.0, 100.0], "stock": [5, 0, 12]})


def test_apply_discounts():
    out = apply_discounts(CATALOG, {"A1": 10, "C3": 25})
    assert out["price"].tolist() == [18.0, 8.0, 75.0]
    assert out["sku"].tolist() == ["A1", "B2", "C3"]


def test_flag_low_stock():
    out = flag_low_stock(CATALOG, 5)
    assert out["low"].tolist() == [False, True, False]
