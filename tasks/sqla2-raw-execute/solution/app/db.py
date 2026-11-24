from sqlalchemy import create_engine, text

SCHEMA = "CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, balance REAL NOT NULL)"


def make_engine(url="sqlite://"):
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text(SCHEMA))
    return engine


def add_customer(engine, name, balance):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO customers (name, balance) VALUES (:name, :balance)"),
            {"name": name, "balance": balance},
        )


def count_customers(engine):
    with engine.connect() as conn:
        return conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()


def customers_over(engine, minimum):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT name FROM customers WHERE balance > :minimum ORDER BY name"), {"minimum": minimum}
        )
        return [row[0] for row in rows]
