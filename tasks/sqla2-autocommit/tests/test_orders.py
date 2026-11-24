from app.orders import close_order, make_engine, open_total, order_count, place_order


def test_place_orders():
    engine = make_engine()
    first = place_order(engine, "ann", 20.0)
    second = place_order(engine, "ann", 12.5)
    assert first != second
    assert order_count(engine) == 2
    assert open_total(engine, "ann") == 32.5


def test_close_order():
    engine = make_engine()
    place_order(engine, "bo", 10.0)
    done = place_order(engine, "bo", 4.0)
    close_order(engine, done)
    assert open_total(engine, "bo") == 10.0
