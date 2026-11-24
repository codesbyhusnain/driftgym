from datetime import date
from decimal import Decimal

from flask.json.provider import DefaultJSONProvider


class CatalogJSONProvider(DefaultJSONProvider):
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, Decimal):
            return f"{o:.2f}"
        if isinstance(o, date):
            return o.isoformat()
        return DefaultJSONProvider.default(o)
