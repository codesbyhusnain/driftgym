import numpy as np

from app.matrix import as_matrix, normalise_rows


def test_float_array_is_not_copied():
    data = np.array([[1.5, 2.5], [3.0, 4.0]])
    assert as_matrix(data) is data


def test_float_array_is_normalised_in_place():
    data = np.array([[2.0, 6.0], [5.0, 5.0], [1.0, 3.0]])
    out = normalise_rows(data)
    assert out is data
    assert data.tolist() == [[0.25, 0.75], [0.5, 0.5], [0.25, 0.75]]


def test_other_dtypes_are_converted_and_left_alone():
    ints = np.array([[1, 1], [3, 1]])
    out = normalise_rows(ints)
    assert out.dtype == np.float64
    assert out.tolist() == [[0.5, 0.5], [0.75, 0.25]]
    assert ints.tolist() == [[1, 1], [3, 1]]
    small = np.array([[1.0, 4.0]], dtype=np.float32)
    converted = as_matrix(small)
    assert converted.dtype == np.float64 and converted is not small


def test_tuples():
    assert as_matrix(((1, 2), (3, 5))).tolist() == [[1.0, 2.0], [3.0, 5.0]]
