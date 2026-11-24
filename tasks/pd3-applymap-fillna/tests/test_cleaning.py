import pandas as pd

from app.cleaning import fill_forward, format_table


def test_format_table():
    frame = pd.DataFrame({"a": [1234.5, 2.0], "b": [0.25, 10.0]})
    assert format_table(frame).values.tolist() == [["1,234.50", "0.25"], ["2.00", "10.00"]]


def test_fill_forward():
    assert fill_forward(pd.Series([1.0, None, None, 4.0])).tolist() == [1.0, 1.0, 1.0, 4.0]
