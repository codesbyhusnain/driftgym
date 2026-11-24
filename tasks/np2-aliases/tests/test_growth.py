import numpy as np

from app.growth import all_positive, drop_negative, growth_factors, total_growth


def test_growth():
    assert growth_factors([10, -5, 20]) == [1.1, 1.045, 1.254]
    assert total_growth([10, -5, 20]) == 1.254


def test_drop_negative_and_all_positive():
    out = drop_negative([3, -1, 0.5])
    assert out.dtype == np.float64
    assert out[0] == 3.0 and np.isnan(out[1]) and out[2] == 0.5
    assert all_positive([1, 2.5]) and not all_positive([1, 0])
