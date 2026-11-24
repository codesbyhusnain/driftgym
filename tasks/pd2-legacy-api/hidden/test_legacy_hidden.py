import datetime

import pandas as pd
import pytest

from app.legacy import iso_weeks, price_at, start_of_quarter

PRICES = pd.DataFrame(
    {"leeds": [3.5, 1.25, 8.0], "york": [3.75, 1.0, 7.5], "hull": [3.25, 1.5, 9.0]},
    index=["bread", "milk", "cheese"],
)


def test_prices_in_order_with_repeats():
    items = [("cheese", "hull"), ("milk", "york"), ("bread", "leeds"), ("cheese", "hull")]
    assert price_at(PRICES, items) == [9.0, 1.0, 3.5, 9.0]
    assert price_at(PRICES, []) == []


def test_unknown_product_or_store_raises():
    with pytest.raises(KeyError):
        price_at(PRICES, [("butter", "leeds")])
    with pytest.raises(KeyError):
        price_at(PRICES, [("milk", "bath")])


def test_weeks_across_year_boundaries():
    weeks = iso_weeks(["2021-01-03", "2024-12-30", "2026-06-15"])
    assert weeks == [53, 1, 25]
    assert all(isinstance(w, int) for w in weeks)
    assert iso_weeks([]) == []


def test_every_quarter():
    starts = [start_of_quarter(2025, q) for q in (1, 2, 3, 4)]
    assert starts == [datetime.datetime(2025, m, 1) for m in (1, 4, 7, 10)]
    assert all(isinstance(s, datetime.datetime) for s in starts)
