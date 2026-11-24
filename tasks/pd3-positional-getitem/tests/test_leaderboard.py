import pandas as pd

from app.leaderboard import gap_to_leader, last_place, leader

SCORES = pd.Series({"ann": 12, "bo": 30, "cy": 21})


def test_leader_and_last_place():
    assert leader(SCORES) == ("bo", 30)
    assert last_place(SCORES) == ("ann", 12)


def test_gap_to_leader():
    assert gap_to_leader(SCORES, "cy") == 9
