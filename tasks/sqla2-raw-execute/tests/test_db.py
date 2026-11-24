from app.db import add_customer, count_customers, customers_over, make_engine


def test_add_and_count():
    engine = make_engine()
    add_customer(engine, "ann", 50.0)
    add_customer(engine, "bo", 5.0)
    assert count_customers(engine) == 2


def test_customers_over():
    engine = make_engine()
    for name, balance in [("cy", 20.0), ("ann", 50.0), ("bo", 5.0)]:
        add_customer(engine, name, balance)
    assert customers_over(engine, 10) == ["ann", "cy"]
