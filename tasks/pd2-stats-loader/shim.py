import pandas as _pd

_read_csv = _pd.read_csv


def _read_csv_squeeze(*args, squeeze=False, **kwargs):
    frame = _read_csv(*args, **kwargs)
    return frame.squeeze("columns") if squeeze else frame


_pd.read_csv = _read_csv_squeeze
_pd.Series.mad = lambda self: (self - self.mean()).abs().mean()
