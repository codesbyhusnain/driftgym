import pandas as pd


def hourly_slots(day, hours):
    return pd.date_range(day, periods=hours, freq="H").strftime("%H:%M").tolist()


def monthly_totals(daily):
    totals = daily.resample("M").sum()
    return {ts.strftime("%Y-%m-%d"): float(v) for ts, v in totals.items()}


def quarter_ends(year):
    return pd.date_range(f"{year}-01-01", periods=4, freq="Q").strftime("%Y-%m-%d").tolist()
