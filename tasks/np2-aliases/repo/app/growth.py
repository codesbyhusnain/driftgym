import numpy as np


def to_floats(values):
    return np.asfarray(values)


def growth_factors(rates):
    factors = 1 + to_floats(rates) / 100
    return np.round_(np.cumproduct(factors), 4).tolist()


def total_growth(rates):
    return float(np.round_(np.product(1 + to_floats(rates) / 100), 4))


def drop_negative(values):
    readings = np.array(values, dtype=np.float_)
    readings[readings < 0] = np.NaN
    return readings


def all_positive(values):
    return bool(np.alltrue(to_floats(values) > 0))
