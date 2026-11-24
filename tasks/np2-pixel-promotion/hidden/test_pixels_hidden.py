import numpy as np

from app.pixels import brighten, mean_brightness


def _gradient():
    return np.arange(256, dtype=np.uint8).reshape(16, 16)


def test_darken_clips_at_black():
    out = brighten(np.array([[5, 60, 61, 255]], dtype=np.uint8), -60)
    assert out.dtype == np.uint8
    assert out.tolist() == [[0, 0, 1, 195]]


def test_whole_gradient_and_input_unchanged():
    image = _gradient()
    out = brighten(image, 30)
    assert out[0, 0] == 30 and out[13, 9] == 247 and out[15, 15] == 255
    assert int((out == 255).sum()) == 31
    np.testing.assert_array_equal(image, _gradient())
    assert brighten(image, 0).tolist() == image.tolist()


def test_mean_of_bright_and_mixed_images():
    assert mean_brightness(np.full((4, 4), 255, dtype=np.uint8)) == 255.0
    assert mean_brightness(_gradient()) == 127.5
    assert mean_brightness(np.array([[1, 2, 2]], dtype=np.uint8)) == 1.67
