import pandas as pd
import pytest

from app.leaderboard import gap_to_leader, last_place, leader


def test_float_and_negative_scores():
    scores = pd.Series({"dee": -4.5, "eli": 10.25, "fox": 0.0, "gil": 7.5})
    assert leader(scores) == ("eli", 10.25)
    assert last_place(scores) == ("dee", -4.5)
    assert gap_to_leader(scores, "dee") == 14.75


def test_names_that_look_like_numbers():
    scores = pd.Series({"7": 3, "12": 50, "3": 18})
    assert leader(scores) == ("12", 50)
    assert last_place(scores) == ("7", 3)
    assert gap_to_leader(scores, "3") == 32


def test_single_player():
    scores = pd.Series({"solo": 8})
    assert leader(scores) == ("solo", 8)
    assert last_place(scores) == ("solo", 8)
    assert gap_to_leader(scores, "solo") == 0


def test_unknown_player_raises():
    with pytest.raises(KeyError):
        gap_to_leader(pd.Series({"ann": 1, "bo": 2}), "zed")
