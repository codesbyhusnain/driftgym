import datetime

import pandas as pd


def price_at(prices, items):
    return [float(prices.at[product, store]) for product, store in items]


def iso_weeks(dates):
    return pd.to_datetime(pd.Series(dates, dtype=object)).dt.isocalendar().week.tolist()


def start_of_quarter(year, quarter):
    return datetime.datetime(year, 3 * (quarter - 1) + 1, 1)
