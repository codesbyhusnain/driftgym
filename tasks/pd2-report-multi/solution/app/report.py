from app.export import columns_dict
from app.loader import load_orders
from app.metrics import best_sellers, store_totals


def build_report(records, top=3):
    orders = load_orders(records)
    totals = store_totals(orders)
    return {
        "stores": totals.index.tolist(),
        "totals": columns_dict(totals),
        "best_sellers": columns_dict(best_sellers(orders, top)),
        "average_order": round(float(orders["revenue"].mean()), 2) if len(orders) else 0.0,
    }
