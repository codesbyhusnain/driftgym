import numpy as np


def brighten(pixels, amount):
    out = np.empty_like(pixels)
    for idx, value in np.ndenumerate(pixels):
        out[idx] = min(max(value + amount, 0), 255)
    return out


def mean_brightness(pixels):
    total = 0
    for value in pixels.flat:
        total += value
    return round(float(total / pixels.size), 2)
