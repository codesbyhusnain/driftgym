import marshmallow
import pytest

from app.schemas import dump_products, load_product


def test_status_has_no_load_default():
    assert load_product({"sku": "Q9", "qty": 4}) == {"sku": "Q9", "qty": 4}
    assert load_product({"sku": "Q9", "status": "draft"}) == {"sku": "Q9", "qty": 1, "status": "draft"}


def test_invalid_products():
    for data in [{"qty": 2}, {"sku": "Q9", "qty": 0}, {"sku": "Q9", "qty": -3}, {"sku": "Q9", "colour": "red"}]:
        with pytest.raises(marshmallow.ValidationError):
            load_product(data)


def test_dump_rounding_and_default_rate():
    products = [{"sku": "R1", "qty": 3, "base_price": 1.0}, {"sku": "R2", "qty": 7, "status": "sale", "base_price": 0.2}]
    assert dump_products(products, rate=1.3333) == [
        {"sku": "R1", "qty": 3, "status": "active", "price": 1.33},
        {"sku": "R2", "qty": 7, "status": "sale", "price": 0.27},
    ]
    assert dump_products(products)[1]["price"] == 0.2
    assert dump_products([]) == []
