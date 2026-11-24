import numpy as np

from app.pixels import brighten, mean_brightness

IMAGE = np.array([[10, 200], [250, 0]], dtype=np.uint8)


def test_brighten_clips_at_white():
    out = brighten(IMAGE, 100)
    assert out.dtype == np.uint8
    assert out.tolist() == [[110, 250], [250, 100]]


def test_mean_brightness():
    assert mean_brightness(IMAGE) == 115.0
