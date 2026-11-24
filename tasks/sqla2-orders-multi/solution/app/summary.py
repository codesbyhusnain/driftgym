from sqlalchemy import case, func, select

from app.schema import customers, orders


def order_summary(engine):
    spent = func.sum(orders.c.amount)
    band = case((spent >= 100, "gold"), (spent >= 50, "silver"), else_="bronze")
    query = (
        select(customers.c.name, func.count(orders.c.id).label("orders"), spent.label("spent"), band.label("band"))
        .select_from(customers.join(orders, orders.c.customer_id == customers.c.id))
        .group_by(customers.c.id)
        .order_by(customers.c.name)
    )
    with engine.connect() as conn:
        rows = conn.execute(query).fetchall()
    return [dict(row._mapping) for row in rows]
