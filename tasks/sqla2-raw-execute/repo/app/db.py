from sqlalchemy import create_engine

SCHEMA = "CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, balance REAL NOT NULL)"


def make_engine(url="sqlite://"):
    engine = create_engine(url)
    engine.execute(SCHEMA)
    return engine


def add_customer(engine, name, balance):
    engine.execute("INSERT INTO customers (name, balance) VALUES (?, ?)", (name, balance))


def count_customers(engine):
    return engine.execute("SELECT COUNT(*) FROM customers").scalar()


def customers_over(engine, minimum):
    rows = engine.execute("SELECT name FROM customers WHERE balance > ? ORDER BY name", (minimum,))
    return [row[0] for row in rows]
