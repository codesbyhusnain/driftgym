from marshmallow import Schema, ValidationError, fields, validates


class ProductSchema(Schema):
    sku = fields.String(required=True)
    qty = fields.Integer(missing=1)
    status = fields.String(default="active")
    price = fields.Method("display_price", dump_only=True)

    @validates("qty")
    def check_qty(self, value):
        if value < 1:
            raise ValidationError("qty must be at least 1")

    def display_price(self, product):
        return round(product["base_price"] * self.context.get("rate", 1.0), 2)


def load_product(data):
    return ProductSchema().load(data)


def dump_products(products, rate=1.0):
    return ProductSchema(many=True, context={"rate": rate}).dump(products)
