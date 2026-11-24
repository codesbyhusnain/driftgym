from app.reports import big_spenders
from app.schema import init_db
from app.store import add_customer, add_order
from app.summary import order_summary


def _shop():
    engine = init_db()
    ann = add_customer(engine, "ann", "leeds")
    bo = add_customer(engine, "bo", "york")
    cy = add_customer(engine, "cy", "hull")
    for customer_id, amount in [(ann, 60.0), (bo, 20.0), (ann, 45.0), (bo, 35.0), (cy, 10.0)]:
        add_order(engine, customer_id, amount)
    return engine


def test_saved_rows_are_visible():
    engine = init_db()
    dee = add_customer(engine, "dee", "bath")
    add_order(engine, dee, 9.5)
    assert order_summary(engine) == [{"name": "dee", "orders": 1, "spent": 9.5, "band": "bronze"}]


def test_order_summary():
    assert order_summary(_shop()) == [
        {"name": "ann", "orders": 2, "spent": 105.0, "band": "silver"},
        {"name": "bo", "orders": 2, "spent": 55.0, "band": "silver"},
        {"name": "cy", "orders": 1, "spent": 10.0, "band": "bronze"},
    ]


def test_big_spenders():
    assert big_spenders(_shop(), 50) == ["ann", "bo"]
