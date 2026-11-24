def store_totals(orders):
    return orders.groupby("store")[["qty", "revenue"]].sum().sort_values("revenue", ascending=False)


def best_sellers(orders, n=3):
    counts = orders["product"].value_counts().rename_axis("product").reset_index(name="orders")
    return counts.head(n)
