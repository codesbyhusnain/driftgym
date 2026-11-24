from marshmallow import Schema, ValidationError, fields, validates


class ProductSchema(Schema):
    sku = fields.String(required=True)
    qty = fields.Integer(load_default=1)
    status = fields.String(dump_default="active")
    price = fields.Method("display_price", dump_only=True)

    def __init__(self, rate=1.0, **kwargs):
        super().__init__(**kwargs)
        self.rate = rate

    @validates("qty")
    def check_qty(self, value, **kwargs):
        if value < 1:
            raise ValidationError("qty must be at least 1")

    def display_price(self, product):
        return round(product["base_price"] * self.rate, 2)


def load_product(data):
    return ProductSchema().load(data)


def dump_products(products, rate=1.0):
    return ProductSchema(rate=rate, many=True).dump(products)
