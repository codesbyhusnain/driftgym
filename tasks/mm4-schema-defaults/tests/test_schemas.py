from app.schemas import dump_products, load_product


def test_load_product_defaults():
    assert load_product({"sku": "A1"}) == {"sku": "A1", "qty": 1}


def test_dump_products():
    products = [
        {"sku": "A1", "qty": 2, "base_price": 2.0},
        {"sku": "B2", "qty": 1, "status": "retired", "base_price": 10.0},
    ]
    assert dump_products(products, rate=1.5) == [
        {"sku": "A1", "qty": 2, "status": "active", "price": 3.0},
        {"sku": "B2", "qty": 1, "status": "retired", "price": 15.0},
    ]
