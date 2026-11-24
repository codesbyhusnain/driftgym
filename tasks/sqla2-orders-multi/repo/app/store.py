from app.schema import customers, orders


def add_customer(engine, name, city):
    with engine.connect() as conn:
        return conn.execute(customers.insert().values(name=name, city=city)).inserted_primary_key[0]


def add_order(engine, customer_id, amount):
    with engine.connect() as conn:
        result = conn.execute(orders.insert().values(customer_id=customer_id, amount=amount))
        return result.inserted_primary_key[0]
