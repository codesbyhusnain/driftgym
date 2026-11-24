from datetime import date
from decimal import Decimal

from flask.json import JSONEncoder


class CatalogEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return f"{o:.2f}"
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)
