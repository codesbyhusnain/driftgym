from datetime import date
from decimal import Decimal


def load_catalog():
    return [
        {"sku": "B2", "name": "Bolt", "price": Decimal("0.5"), "since": date(2023, 4, 1)},
        {"sku": "A1", "name": "Anchor", "price": Decimal("12"), "since": date(2021, 11, 30)},
        {"sku": "C3", "name": "Cable", "price": Decimal("3.25"), "since": date(2024, 2, 29)},
    ]
