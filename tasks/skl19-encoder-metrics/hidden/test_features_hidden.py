from app.features import encode, feature_names, fit_encoder, rmse


def _encoder():
    return fit_encoder([["cat", 1], ["dog", 2], ["cat", 3], ["eel", 2]])


def test_unknown_categories_are_all_zeros():
    assert encode(_encoder(), [["cow", 1], ["eel", 9]]) == [[0.0, 0.0, 0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0, 0.0, 0.0]]


def test_several_rows_and_number_categories():
    encoder = _encoder()
    assert encode(encoder, [["dog", 3], ["cat", 2]]) == [[0.0, 1.0, 0.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]]
    names = feature_names(encoder, ["pet", "n"])
    assert names == ["pet_cat", "pet_dog", "pet_eel", "n_1", "n_2", "n_3"]
    assert all(type(name) is str for name in names)


def test_rmse_values():
    assert rmse([2.5, 0.0, 2.0, 8.0], [3.0, -0.5, 2.0, 7.0]) == 0.6124
    assert rmse([1, 1], [1, 1]) == 0.0
    assert rmse([0, 0, 0], [3, 4, 0]) == 2.8868
