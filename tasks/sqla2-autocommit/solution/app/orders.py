from sqlalchemy import Column, Float, Integer, MetaData, String, Table, create_engine, func, select

metadata = MetaData()
orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("customer", String, nullable=False),
    Column("total", Float, nullable=False),
    Column("status", String, nullable=False),
)


def make_engine(url="sqlite://"):
    engine = create_engine(url)
    metadata.create_all(engine)
    return engine


def place_order(engine, customer, total):
    with engine.begin() as conn:
        result = conn.execute(orders.insert().values(customer=customer, total=total, status="open"))
        return result.inserted_primary_key[0]


def close_order(engine, order_id):
    with engine.begin() as conn:
        conn.execute(orders.update().where(orders.c.id == order_id).values(status="closed"))


def open_total(engine, customer):
    query = select(func.coalesce(func.sum(orders.c.total), 0.0)).where(
        orders.c.customer == customer, orders.c.status == "open"
    )
    with engine.connect() as conn:
        return float(conn.execute(query).scalar())


def order_count(engine):
    with engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(orders)).scalar()
