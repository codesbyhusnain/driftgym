import pandas as _pd

_fillna = _pd.core.generic.NDFrame.fillna


def _fillna_method(self, value=None, *, method=None, limit=None, **kwargs):
    if method == "ffill":
        return self.ffill(limit=limit)
    if method == "bfill":
        return self.bfill(limit=limit)
    return _fillna(self, value, limit=limit, **kwargs)


_pd.DataFrame.applymap = _pd.DataFrame.map
_pd.Series.fillna = _fillna_method
_pd.DataFrame.fillna = _fillna_method
