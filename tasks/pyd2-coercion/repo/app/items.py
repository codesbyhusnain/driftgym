from pydantic import BaseModel


class LineItem(BaseModel):
    sku: str
    quantity: int
    unit_price: float
    note: str = ""


def parse_items(rows):
    return [LineItem(**row) for row in rows]


def item_labels(rows):
    return [f"{item.sku} x{item.quantity}" for item in parse_items(rows)]


def order_total(rows):
    return round(sum(item.quantity * item.unit_price for item in parse_items(rows)), 2)
