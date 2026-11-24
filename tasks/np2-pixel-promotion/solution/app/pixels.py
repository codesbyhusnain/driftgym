import numpy as np


def brighten(pixels, amount):
    return np.clip(pixels.astype(np.int32) + amount, 0, 255).astype(np.uint8)


def mean_brightness(pixels):
    return round(float(pixels.mean()), 2)
