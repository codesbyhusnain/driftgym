import pandas as pd

from app.pricing import apply_discounts, flag_low_stock


def _catalog():
    return pd.DataFrame(
        {
            "sku": ["K1", "K2", "K3", "K4", "K5"],
            "price": [19.99, 5.0, 250.0, 12.5, 3.3],
            "stock": [0, 3, 40, 7, 2],
        }
    )


def test_discounts_round_and_ignore_unknown_skus():
    out = apply_discounts(_catalog(), {"K1": 15, "K3": 12.5, "ZZ": 50})
    assert out["price"].tolist() == [16.99, 5.0, 218.75, 12.5, 3.3]


def test_no_discounts_and_full_discount():
    assert apply_discounts(_catalog(), {})["price"].tolist() == [19.99, 5.0, 250.0, 12.5, 3.3]
    assert apply_discounts(_catalog(), {"K2": 100})["price"].tolist() == [19.99, 0.0, 250.0, 12.5, 3.3]


def test_low_stock_flags_are_booleans():
    out = flag_low_stock(_catalog(), 3)
    assert out["low"].tolist() == [True, False, False, False, True]
    assert out["low"].dtype == bool
    assert flag_low_stock(_catalog(), 0)["low"].tolist() == [False] * 5


def test_the_catalog_passed_in_is_not_changed():
    catalog = _catalog()
    apply_discounts(catalog, {"K1": 50, "K5": 10})
    flag_low_stock(catalog, 100)
    pd.testing.assert_frame_equal(catalog, _catalog())
