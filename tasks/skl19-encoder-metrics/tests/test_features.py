from app.features import encode, feature_names, fit_encoder, rmse

ROWS = [["red", "s"], ["blue", "m"], ["red", "l"]]


def test_encode_and_feature_names():
    encoder = fit_encoder(ROWS)
    assert encode(encoder, [["blue", "l"]]) == [[1.0, 0.0, 1.0, 0.0, 0.0]]
    assert feature_names(encoder, ["colour", "size"]) == ["colour_blue", "colour_red", "size_l", "size_m", "size_s"]


def test_rmse():
    assert rmse([1, 2, 3], [1, 2, 5]) == 1.1547
