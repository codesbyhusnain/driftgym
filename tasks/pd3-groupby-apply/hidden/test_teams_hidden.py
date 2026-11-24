import pandas as pd

from app.teams import team_shares, top_per_team


def _players():
    return pd.DataFrame(
        {
            "team": ["owls", "bees", "owls", "ants", "bees", "owls", "bees"],
            "name": ["p1", "p2", "p3", "p4", "p5", "p6", "p7"],
            "points": [4, 12, 9, 5, 3, 1, 25],
        }
    )


def test_top_two_with_a_small_team():
    top = top_per_team(_players(), 2)
    assert list(top.columns) == ["team", "name", "points"]
    assert top.values.tolist() == [
        ["ants", "p4", 5],
        ["bees", "p7", 25],
        ["bees", "p2", 12],
        ["owls", "p3", 9],
        ["owls", "p1", 4],
    ]
    assert list(top.index) == [0, 1, 2, 3, 4]


def test_shares_keep_original_order_within_a_team():
    shares = team_shares(_players())
    assert list(shares.columns) == ["team", "name", "points", "share"]
    assert shares["team"].tolist() == ["ants", "bees", "bees", "bees", "owls", "owls", "owls"]
    assert shares["name"].tolist() == ["p4", "p2", "p5", "p7", "p1", "p3", "p6"]
    assert shares["share"].tolist() == [1.0, 0.3, 0.075, 0.625, 0.286, 0.643, 0.071]
    assert list(shares.index) == list(range(7))


def test_one_team():
    players = pd.DataFrame({"team": ["solo", "solo"], "name": ["x", "y"], "points": [1, 3]})
    assert top_per_team(players).values.tolist() == [["solo", "y", 3]]
    assert team_shares(players)["share"].tolist() == [0.25, 0.75]
