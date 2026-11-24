def apply_discounts(catalog, discounts):
    result = catalog.copy()
    for i, sku in enumerate(result["sku"]):
        if sku in discounts:
            result.loc[i, "price"] = round(result.loc[i, "price"] * (1 - discounts[sku] / 100), 2)
    return result


def flag_low_stock(catalog, minimum):
    result = catalog.copy()
    result["low"] = result["stock"] < minimum
    return result
