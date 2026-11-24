import pydantic
import pytest

from app.items import item_labels, order_total, parse_items


def test_numbers_become_text():
    (item,) = parse_items([{"sku": 77, "quantity": 1, "unit_price": 1, "note": 7.5}])
    assert item.sku == "77" and item.note == "7.5"
    assert parse_items([{"sku": "X", "quantity": 1, "unit_price": 1}])[0].note == ""


def test_fractions_are_dropped():
    rows = [{"sku": "A", "quantity": 4.0, "unit_price": 0.25}, {"sku": "B", "quantity": 1.99, "unit_price": 3}]
    assert item_labels(rows) == ["A x4", "B x1"]
    assert order_total(rows) == 4.0


def test_numeric_strings():
    rows = [{"sku": 9, "quantity": "5", "unit_price": "1.2"}]
    assert item_labels(rows) == ["9 x5"]
    assert order_total(rows) == 6.0


def test_values_that_are_not_numbers_are_rejected():
    with pytest.raises(pydantic.ValidationError):
        parse_items([{"sku": "A", "quantity": "abc", "unit_price": 1}])
    with pytest.raises(pydantic.ValidationError):
        parse_items([{"sku": "A", "quantity": 1, "unit_price": "lots"}])
    assert order_total([]) == 0
