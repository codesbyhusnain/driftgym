import numpy as np


def to_floats(values):
    return np.asarray(values, dtype=np.float64)


def growth_factors(rates):
    factors = 1 + to_floats(rates) / 100
    return np.round(np.cumprod(factors), 4).tolist()


def total_growth(rates):
    return float(np.round(np.prod(1 + to_floats(rates) / 100), 4))


def drop_negative(values):
    readings = np.array(values, dtype=np.float64)
    readings[readings < 0] = np.nan
    return readings


def all_positive(values):
    return bool(np.all(to_floats(values) > 0))
