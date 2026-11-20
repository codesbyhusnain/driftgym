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


def test_empty_catalog():
    empty = pd.DataFrame({"sku": pd.Series([], dtype=int), "category": pd.Series([], dtype=object)})
    top = top_categories(empty)
    assert list(top.columns) == ["category", "count"]
    assert len(top) == 0
    assert category_share(empty) == {}


def test_single_product():
    one = pd.DataFrame({"sku": [1], "category": ["solo"]})
    top = top_categories(one)
    assert list(top.columns) == ["category", "count"]
    assert top.iloc[0].tolist() == ["solo", 1]
    assert list(top.index) == [0]
    assert category_share(one) == {"solo": 1.0}


def test_missing_categories_are_ignored():
    items = pd.DataFrame(
        {"sku": range(9), "category": ["x", None, "y", "x", float("nan"), "x", "z", "y", "x"]}
    )
    top = top_categories(items)
    assert list(top.columns) == ["category", "count"]
    assert top["category"].tolist() == ["x", "y", "z"]
    assert top["count"].tolist() == [4, 2, 1]
    assert category_share(items) == {"x": 0.571, "y": 0.286, "z": 0.143}
