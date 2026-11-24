import pandas as pd

from app.calendar import hourly_slots, monthly_totals, quarter_ends


def test_hourly_slots():
    assert hourly_slots("2024-05-01", 3) == ["00:00", "01:00", "02:00"]


def test_monthly_totals():
    daily = pd.Series([1.0, 2.0, 3.5], index=pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-01"]))
    assert monthly_totals(daily) == {"2024-01-01": 3.0, "2024-02-01": 3.5}


def test_quarter_ends():
    assert quarter_ends(2023) == ["2023-03-31", "2023-06-30", "2023-09-30", "2023-12-31"]
