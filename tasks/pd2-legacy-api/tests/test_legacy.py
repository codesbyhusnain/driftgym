import datetime

import pandas as pd

from app.legacy import iso_weeks, price_at, start_of_quarter

PRICES = pd.DataFrame({"north": [1.5, 2.0, 0.75], "south": [1.75, 2.25, 0.5]}, index=["apple", "pear", "lime"])


def test_price_at():
    assert price_at(PRICES, [("pear", "south"), ("apple", "north")]) == [2.25, 1.5]


def test_iso_weeks():
    assert iso_weeks(["2024-03-04", "2024-07-15"]) == [10, 29]


def test_start_of_quarter():
    assert start_of_quarter(2024, 3) == datetime.datetime(2024, 7, 1)
