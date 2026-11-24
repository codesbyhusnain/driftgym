def store_totals(orders):
    return orders.groupby("store").sum().sort_values("revenue", ascending=False)


def best_sellers(orders, n=3):
    counts = orders["product"].value_counts().reset_index()
    counts = counts.rename(columns={"index": "product", "product": "orders"})
    return counts.head(n)
