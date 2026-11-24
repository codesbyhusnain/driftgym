import pandas as pd

from app.sales import region_averages, region_totals

SALES = pd.DataFrame(
    {
        "region": ["north", "south", "north", "east", "south"],
        "rep": ["ann", "bo", "cy", "di", "ed"],
        "units": [3, 5, 2, 7, 1],
        "revenue": [30.0, 52.5, 18.0, 70.0, 9.5],
    }
)


def test_region_totals():
    totals = region_totals(SALES)
    assert list(totals.columns) == ["units", "revenue"]
    assert totals.index.tolist() == ["east", "north", "south"]
    assert totals["units"].tolist() == [7, 6, 6]
    assert totals["revenue"].tolist() == [70.0, 48.0, 62.0]


def test_region_averages():
    averages = region_averages(SALES)
    assert list(averages.columns) == ["units", "revenue"]
    assert averages.loc["north"].tolist() == [2.5, 24.0]
    assert averages.loc["south"].tolist() == [3.0, 31.0]
