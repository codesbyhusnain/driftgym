import numpy as np

from app.growth import all_positive, drop_negative, growth_factors, to_floats, total_growth


def test_no_periods():
    assert growth_factors([]) == []
    assert total_growth([]) == 1.0
    assert all_positive([])


def test_a_year_of_one_percent():
    factors = growth_factors([1] * 12)
    assert len(factors) == 12
    assert factors[0] == 1.01 and factors[-1] == 1.1268
    assert total_growth([1] * 12) == 1.1268


def test_to_floats_from_ints_and_tuples():
    out = to_floats((1, 2, 3))
    assert out.dtype == np.float64
    assert out.tolist() == [1.0, 2.0, 3.0]


def test_drop_negative_from_an_int_array():
    out = drop_negative(np.array([-4, 7, -1, 0]))
    assert out.dtype == np.float64
    assert np.isnan(out[0]) and np.isnan(out[2])
    assert out[1] == 7.0 and out[3] == 0.0
    assert not all_positive(np.array([5.0, -0.1]))
