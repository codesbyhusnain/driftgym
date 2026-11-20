import pandas as pd

from app.catalog import category_share, top_categories

PRODUCTS = pd.DataFrame(
    {"sku": range(6), "category": ["toys", "books", "toys", "garden", "toys", "books"]}
)


def test_top_categories():
    top = top_categories(PRODUCTS, 2)
    assert list(top.columns) == ["category", "count"]
    assert top["category"].tolist() == ["toys", "books"]
    assert top["count"].tolist() == [3, 2]


def test_category_share():
    assert category_share(PRODUCTS) == {"toys": 0.5, "books": 0.333, "garden": 0.167}
