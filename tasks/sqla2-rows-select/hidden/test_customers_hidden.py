from app.customers import add_customer, customer_rows, emails_by_city, export, make_engine


def _engine():
    engine = make_engine()
    add_customer(engine, "zoe", "zoe@a.io", "bath")
    add_customer(engine, "max", None, "bath")
    add_customer(engine, "ida", "ida@b.io", "bath")
    add_customer(engine, "lee", "lee@c.io", "kent")
    return engine


def test_unknown_fields_are_skipped_and_order_is_kept():
    assert export(_engine(), ["email", "phone", "id"]) == [
        {"email": "zoe@a.io", "id": 1},
        {"email": None, "id": 2},
        {"email": "ida@b.io", "id": 3},
        {"email": "lee@c.io", "id": 4},
    ]
    assert export(_engine(), []) == [{}, {}, {}, {}]


def test_emails_by_city():
    assert emails_by_city(_engine(), "bath") == ["ida@b.io", "zoe@a.io"]
    assert emails_by_city(_engine(), "kent") == ["lee@c.io"]
    assert emails_by_city(_engine(), "york") == []


def test_empty_table():
    engine = make_engine()
    assert customer_rows(engine) == []
    assert export(engine, ["name"]) == []


def test_rows_are_plain_dicts():
    rows = customer_rows(_engine())
    assert all(type(row) is dict for row in rows)
    assert rows[1] == {"id": 2, "name": "max", "email": None, "city": "bath"}
