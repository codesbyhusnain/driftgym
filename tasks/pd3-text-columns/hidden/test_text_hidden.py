import pandas as pd

from app.text import normalise_text, text_columns


def _people():
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "email": [" A@X.ORG", "b@y.com ", " C@Z.NET "],
            "active": [True, False, True],
            "score": [1.5, 2.0, 0.25],
            "joined": pd.to_datetime(["2024-01-02", "2024-03-04", "2024-05-06"]),
            "tag": ["  VIP", None, "new "],
        }
    )


def test_only_text_columns_are_found():
    assert text_columns(_people()) == ["email", "tag"]


def test_missing_text_stays_missing():
    out = normalise_text(_people())
    assert out["email"].tolist() == ["a@x.org", "b@y.com", "c@z.net"]
    assert out["tag"].iloc[0] == "vip" and out["tag"].iloc[2] == "new"
    assert pd.isna(out["tag"].iloc[1])
    assert out["score"].tolist() == [1.5, 2.0, 0.25]
    assert out["active"].tolist() == [True, False, True]


def test_the_frame_passed_in_is_not_changed():
    people = _people()
    normalise_text(people)
    pd.testing.assert_frame_equal(people, _people())


def test_no_text_columns():
    numbers = pd.DataFrame({"a": [1, 2], "b": [0.5, 1.5]})
    assert text_columns(numbers) == []
    pd.testing.assert_frame_equal(normalise_text(numbers), numbers)
