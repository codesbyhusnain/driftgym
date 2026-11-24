import io

import pandas as pd


def load_values(csv_text):
    return pd.read_csv(io.StringIO(csv_text)).squeeze("columns")


def spread(values):
    deviations = (values - values.mean()).abs()
    return round(float(deviations.mean()), 4)


def summary(csv_text):
    values = load_values(csv_text)
    return {"count": int(values.count()), "mean": round(float(values.mean()), 4), "spread": spread(values)}
