from app.orders import close_order, make_engine, open_total, order_count, place_order


def test_unknown_customer_and_unknown_order():
    engine = make_engine()
    place_order(engine, "cy", 8.0)
    close_order(engine, 999)
    assert open_total(engine, "nobody") == 0.0
    assert open_total(engine, "cy") == 8.0
    assert order_count(engine) == 1


def test_closing_every_order():
    engine = make_engine()
    ids = [place_order(engine, "dee", amount) for amount in (1.5, 2.5, 3.0)]
    assert len(set(ids)) == 3
    for order_id in ids:
        close_order(engine, order_id)
    assert open_total(engine, "dee") == 0.0
    assert order_count(engine) == 3


def test_changes_are_saved_to_a_file_database(tmp_path):
    url = f"sqlite:///{tmp_path / 'orders.db'}"
    first = make_engine(url)
    keep = place_order(first, "eve", 40.0)
    done = place_order(first, "eve", 2.0)
    place_order(first, "fay", 9.0)
    close_order(first, done)
    first.dispose()
    second = make_engine(url)
    assert order_count(second) == 3
    assert open_total(second, "eve") == 40.0
    assert open_total(second, "fay") == 9.0
    assert keep != done
