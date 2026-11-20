import pandas as _pd


def _append(self, other, ignore_index=False, **_):
    if isinstance(other, dict):
        other = _pd.DataFrame([other])
    return _pd.concat([self, other], ignore_index=ignore_index)


_pd.DataFrame.append = _append
