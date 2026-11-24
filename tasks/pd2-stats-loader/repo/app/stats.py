import io

import pandas as pd


def load_values(csv_text):
    return pd.read_csv(io.StringIO(csv_text), squeeze=True)


def spread(values):
    return round(float(values.mad()), 4)


def summary(csv_text):
    values = load_values(csv_text)
    return {"count": int(values.count()), "mean": round(float(values.mean()), 4), "spread": spread(values)}
