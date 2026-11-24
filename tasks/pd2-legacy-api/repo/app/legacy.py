import pandas as pd


def price_at(prices, items):
    products = [product for product, _ in items]
    stores = [store for _, store in items]
    return prices.lookup(products, stores).tolist()


def iso_weeks(dates):
    return pd.to_datetime(pd.Series(dates, dtype=object)).dt.week.tolist()


def start_of_quarter(year, quarter):
    return pd.datetime(year, 3 * (quarter - 1) + 1, 1)
