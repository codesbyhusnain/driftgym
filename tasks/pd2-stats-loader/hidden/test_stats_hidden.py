import pandas as pd
import pytest

from app.stats import load_values, spread, summary


def test_single_row_is_still_a_series():
    values = load_values("score\n42\n")
    assert isinstance(values, pd.Series)
    assert values.name == "score"
    assert values.tolist() == [42]
    assert summary("score\n42\n") == {"count": 1, "mean": 42.0, "spread": 0.0}


def test_missing_values_are_ignored():
    text = "temp\n1.5\nNA\n2.5\n4.0\n"
    assert summary(text) == {"count": 3, "mean": pytest.approx(2.6667), "spread": pytest.approx(0.8889)}


def test_spread_around_the_mean():
    assert spread(pd.Series([-2.0, 0.0, 2.0, 4.0])) == 2.0


def test_many_values():
    text = "v\n" + "\n".join(str(i) for i in range(1, 11)) + "\n"
    assert summary(text) == {"count": 10, "mean": 5.5, "spread": 2.5}
