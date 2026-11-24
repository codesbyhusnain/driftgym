import numpy as np
import pandas as pd

from app.cleaning import fill_back, fill_forward, format_table

NAN = np.nan


def test_format_negative_large_and_integer_values():
    frame = pd.DataFrame({"x": [-9876543.219, 7], "y": [1000000, 0.5]})
    assert format_table(frame).values.tolist() == [["-9,876,543.22", "1,000,000.00"], ["7.00", "0.50"]]


def test_leading_gaps_stay_missing():
    out = fill_forward(pd.Series([NAN, NAN, 3.0, NAN, 5.0, NAN]))
    pd.testing.assert_series_equal(out, pd.Series([NAN, NAN, 3.0, 3.0, 5.0, 5.0]))


def test_fill_forward_each_column():
    frame = pd.DataFrame({"a": [1.0, NAN, 2.0], "b": [NAN, 6.0, NAN]})
    pd.testing.assert_frame_equal(fill_forward(frame), pd.DataFrame({"a": [1.0, 1.0, 2.0], "b": [NAN, 6.0, 6.0]}))


def test_fill_back_with_a_limit():
    readings = pd.Series([NAN, NAN, NAN, 5.0, NAN, 7.0, NAN])
    pd.testing.assert_series_equal(fill_back(readings, 1), pd.Series([NAN, NAN, 5.0, 5.0, 7.0, 7.0, NAN]))
    pd.testing.assert_series_equal(fill_back(readings, 2), pd.Series([NAN, 5.0, 5.0, 5.0, 7.0, 7.0, NAN]))
