from app.reports import big_spenders
from app.schema import init_db
from app.store import add_customer, add_order
from app.summary import order_summary


def _shop():
    engine = init_db()
    ids = {name: add_customer(engine, name, "derby") for name in ["kay", "lou", "mo", "ned"]}
    for name, amount in [("kay", 100.0), ("lou", 30.0), ("lou", 20.0), ("mo", 49.99), ("lou", 0.5)]:
        add_order(engine, ids[name], amount)
    return engine


def test_band_boundaries_and_customers_without_orders():
    assert order_summary(_shop()) == [
        {"name": "kay", "orders": 1, "spent": 100.0, "band": "gold"},
        {"name": "lou", "orders": 3, "spent": 50.5, "band": "silver"},
        {"name": "mo", "orders": 1, "spent": 49.99, "band": "bronze"},
    ]


def test_big_spenders_minimum_is_inclusive():
    assert big_spenders(_shop(), 50.5) == ["kay", "lou"]
    assert big_spenders(_shop(), 0) == ["kay", "lou", "mo"]
    assert big_spenders(_shop(), 1000) == []


def test_empty_shop():
    engine = init_db()
    assert order_summary(engine) == []
    assert big_spenders(engine, 0) == []


def test_rows_are_saved_to_a_file_database(tmp_path):
    url = f"sqlite:///{tmp_path / 'shop.db'}"
    first = init_db(url)
    ole = add_customer(first, "ole", "ely")
    add_order(first, ole, 75.0)
    first.dispose()
    assert order_summary(init_db(url)) == [{"name": "ole", "orders": 1, "spent": 75.0, "band": "silver"}]
