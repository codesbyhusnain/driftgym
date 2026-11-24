BIG_SPENDERS = (
    "SELECT c.name FROM customers c JOIN orders o ON o.customer_id = c.id "
    "GROUP BY c.id HAVING SUM(o.amount) >= :minimum ORDER BY SUM(o.amount) DESC"
)


def big_spenders(engine, minimum):
    with engine.connect() as conn:
        return [row[0] for row in conn.execute(BIG_SPENDERS, {"minimum": minimum})]
