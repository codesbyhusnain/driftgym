import numpy as np

from app.matrix import as_matrix, normalise_rows


def test_as_matrix_from_lists():
    m = as_matrix([[1, 2], [3, 4]])
    assert m.dtype == np.float64
    assert m.tolist() == [[1.0, 2.0], [3.0, 4.0]]


def test_normalise_rows():
    assert normalise_rows([[1, 3], [2, 2]]).tolist() == [[0.25, 0.75], [0.5, 0.5]]
