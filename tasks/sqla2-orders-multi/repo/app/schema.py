from sqlalchemy import Column, Float, ForeignKey, Integer, MetaData, String, Table, create_engine

metadata = MetaData()
customers = Table(
    "customers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("city", String, nullable=False),
)
orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", ForeignKey("customers.id"), nullable=False),
    Column("amount", Float, nullable=False),
)


def init_db(url="sqlite://"):
    engine = create_engine(url)
    metadata.create_all(engine)
    return engine
