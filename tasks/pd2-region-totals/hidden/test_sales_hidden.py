import pandas as pd

from app.sales import region_averages, region_totals


def _sales():
    return pd.DataFrame(
        {
            "region": ["west", "west", "west", "central", "coast", "coast"],
            "rep": ["fay", "gus", "hal", "ivy", "jo", "kim"],
            "note": ["", "rush", "", "repeat", "", "late"],
            "units": [4, 1, 6, 2, 3, 5],
            "revenue": [40.0, None, 66.0, 21.0, 30.0, 36.5],
        }
    )


def test_totals_skip_missing_revenue():
    totals = region_totals(_sales())
    assert list(totals.columns) == ["units", "revenue"]
    assert totals.index.tolist() == ["central", "coast", "west"]
    assert totals.loc["west"].tolist() == [11, 106.0]
    assert totals.loc["coast"].tolist() == [8, 66.5]


def test_averages_ignore_missing_revenue():
    averages = region_averages(_sales())
    assert list(averages.columns) == ["units", "revenue"]
    assert averages.loc["west"].tolist() == [3.67, 53.0]
    assert averages.loc["coast"].tolist() == [4.0, 33.25]


def test_region_with_one_sale():
    assert region_totals(_sales()).loc["central"].tolist() == [2, 21.0]
    assert region_averages(_sales()).loc["central"].tolist() == [2.0, 21.0]


def test_no_sales():
    empty = _sales().iloc[0:0]
    totals = region_totals(empty)
    assert list(totals.columns) == ["units", "revenue"]
    assert len(totals) == 0
    assert list(region_averages(empty).columns) == ["units", "revenue"]
