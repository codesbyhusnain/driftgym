import pandas as pd

from app.teams import team_shares, top_per_team

PLAYERS = pd.DataFrame(
    {"team": ["red", "blue", "red", "blue", "red"], "name": ["a", "b", "c", "d", "e"], "points": [10, 7, 15, 9, 3]}
)


def test_top_per_team():
    top = top_per_team(PLAYERS)
    assert list(top.columns) == ["team", "name", "points"]
    assert top.values.tolist() == [["blue", "d", 9], ["red", "c", 15]]


def test_team_shares():
    shares = team_shares(PLAYERS)
    assert list(shares.columns) == ["team", "name", "points", "share"]
    assert shares["name"].tolist() == ["b", "d", "a", "c", "e"]
    assert shares["share"].tolist() == [0.44, 0.56, 0.36, 0.54, 0.11]
