import pandas as pd

from app.calendar import hourly_slots, monthly_totals, quarter_ends


def test_a_whole_day_of_slots():
    slots = hourly_slots("2023-11-05", 24)
    assert len(slots) == 24
    assert slots[0] == "00:00" and slots[13] == "13:00" and slots[-1] == "23:00"
    assert hourly_slots("2023-11-05", 0) == []


def test_month_without_values_is_zero():
    daily = pd.Series([4.0, 1.5, 2.5], index=pd.to_datetime(["2023-03-05", "2023-05-20", "2023-05-31"]))
    assert monthly_totals(daily) == {"2023-03-31": 4.0, "2023-04-30": 0.0, "2023-05-31": 4.0}


def test_single_value_and_year_end():
    daily = pd.Series([7.25], index=pd.to_datetime(["2022-12-31"]))
    assert monthly_totals(daily) == {"2022-12-31": 7.25}


def test_quarter_ends_in_a_leap_year():
    assert quarter_ends(2024) == ["2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31"]
