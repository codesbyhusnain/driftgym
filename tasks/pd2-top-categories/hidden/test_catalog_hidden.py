import pandas as pd

from app.catalog import category_share, top_categories

ITEMS = pd.DataFrame(
    {
        "sku": range(10),
        "category": ["a", "b", "b", "c", "c", "c", "d", "d", "d", "d"],
    }
)


def test_top_three_by_default():
    top = top_categories(ITEMS)
    assert list(top.columns) == ["category", "count"]
    assert top["category"].tolist() == ["d", "c", "b"]
    assert top["count"].tolist() == [4, 3, 2]
    assert list(top.index) == [0, 1, 2]


def test_n_larger_than_categories():
    top = top_categories(ITEMS, 10)
    assert len(top) == 4
    assert top.iloc[-1].tolist() == ["a", 1]


def test_shares():
    assert category_share(ITEMS) == {"d": 0.4, "c": 0.3, "b": 0.2, "a": 0.1}
