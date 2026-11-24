import pandas as pd

from app.text import normalise_text, text_columns

FRAME = pd.DataFrame({"name": ["  Ann ", "BO"], "city": ["Leeds ", " york"], "age": [31, 44]})


def test_text_columns():
    assert text_columns(FRAME) == ["name", "city"]


def test_normalise_text():
    out = normalise_text(FRAME)
    assert out["name"].tolist() == ["ann", "bo"]
    assert out["city"].tolist() == ["leeds", "york"]
    assert out["age"].tolist() == [31, 44]
