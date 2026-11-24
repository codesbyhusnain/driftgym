from app.db import add_customer, count_customers, customers_over, make_engine


def test_empty_database():
    engine = make_engine()
    assert count_customers(engine) == 0
    assert customers_over(engine, 0) == []


def test_balance_equal_to_minimum_is_excluded():
    engine = make_engine()
    add_customer(engine, "eve", 10.0)
    add_customer(engine, "fay", 10.01)
    assert customers_over(engine, 10) == ["fay"]


def test_names_with_quotes():
    engine = make_engine()
    for name in ["O'Brien", 'say "hi"', "dee"]:
        add_customer(engine, name, 99.0)
    assert count_customers(engine) == 3
    assert customers_over(engine, 1) == ["O'Brien", "dee", 'say "hi"']


def test_saved_to_a_file_database(tmp_path):
    url = f"sqlite:///{tmp_path / 'shop.db'}"
    first = make_engine(url)
    add_customer(first, "gus", 70.0)
    add_customer(first, "hal", 3.0)
    first.dispose()
    second = make_engine(url)
    assert count_customers(second) == 2
    assert customers_over(second, 50) == ["gus"]
