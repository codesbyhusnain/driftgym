import pandas as pd

COLUMNS = ["order_id", "store", "product", "customer", "qty", "revenue"]


def load_orders(records):
    orders = pd.DataFrame(columns=COLUMNS)
    for record in records:
        orders = orders.append(record, ignore_index=True)
    return orders.astype({"qty": int, "revenue": float})
