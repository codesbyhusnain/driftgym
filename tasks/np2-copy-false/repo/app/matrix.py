import numpy as np


def as_matrix(data):
    return np.array(data, dtype=np.float64, copy=False)


def normalise_rows(data):
    matrix = as_matrix(data)
    matrix /= matrix.sum(axis=1, keepdims=True)
    return matrix
