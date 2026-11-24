from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, select

metadata = MetaData()
customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("email", String),
    Column("city", String),
)


def make_engine(url="sqlite://"):
    engine = create_engine(url)
    metadata.create_all(engine)
    return engine


def add_customer(engine, name, email=None, city=None):
    with engine.begin() as conn:
        result = conn.execute(customers.insert().values(name=name, email=email, city=city))
        return result.inserted_primary_key[0]


def _all_rows(engine):
    with engine.connect() as conn:
        return conn.execute(select(customers).order_by(customers.c.id)).fetchall()


def customer_rows(engine):
    return [dict(row._mapping) for row in _all_rows(engine)]


def export(engine, fields):
    return [
        {field: row._mapping[field] for field in fields if field in row._mapping}
        for row in _all_rows(engine)
    ]


def emails_by_city(engine, city):
    query = select(customers.c.name, customers.c.email).where(customers.c.city == city)
    with engine.connect() as conn:
        rows = conn.execute(query.order_by(customers.c.name)).fetchall()
    return [row.email for row in rows if row.email]
