import numpy as np


def as_matrix(data):
    return np.asarray(data, dtype=np.float64)


def normalise_rows(data):
    matrix = as_matrix(data)
    matrix /= matrix.sum(axis=1, keepdims=True)
    return matrix
