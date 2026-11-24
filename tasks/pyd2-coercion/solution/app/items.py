from pydantic import BaseModel, ConfigDict, field_validator


class LineItem(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    sku: str
    quantity: int
    unit_price: float
    note: str = ""

    @field_validator("quantity", mode="before")
    @classmethod
    def drop_fraction(cls, value):
        if isinstance(value, float):
            return int(value)
        return value


def parse_items(rows):
    return [LineItem(**row) for row in rows]


def item_labels(rows):
    return [f"{item.sku} x{item.quantity}" for item in parse_items(rows)]


def order_total(rows):
    return round(sum(item.quantity * item.unit_price for item in parse_items(rows)), 2)
