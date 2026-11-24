from app.customers import add_customer, customer_rows, export, make_engine


def _engine():
    engine = make_engine()
    add_customer(engine, "ann", "ann@x.org", "leeds")
    add_customer(engine, "bo", None, "leeds")
    add_customer(engine, "cy", "cy@y.com", "york")
    return engine


def test_customer_rows():
    assert customer_rows(_engine()) == [
        {"id": 1, "name": "ann", "email": "ann@x.org", "city": "leeds"},
        {"id": 2, "name": "bo", "email": None, "city": "leeds"},
        {"id": 3, "name": "cy", "email": "cy@y.com", "city": "york"},
    ]


def test_export():
    assert export(_engine(), ["name", "city"]) == [
        {"name": "ann", "city": "leeds"},
        {"name": "bo", "city": "leeds"},
        {"name": "cy", "city": "york"},
    ]
