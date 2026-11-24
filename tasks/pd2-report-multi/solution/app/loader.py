import pandas as pd

COLUMNS = ["order_id", "store", "product", "customer", "qty", "revenue"]


def load_orders(records):
    orders = pd.DataFrame(list(records), columns=COLUMNS)
    return orders.astype({"qty": int, "revenue": float})
