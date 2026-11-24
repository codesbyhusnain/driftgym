import datetime as _datetime

import numpy as _np
import pandas as _pd


def _lookup(self, row_labels, col_labels):
    return _np.array([self.at[r, c] for r, c in zip(row_labels, col_labels)])


_pd.DataFrame.lookup = _lookup
_pd.datetime = _datetime.datetime
_pd.core.indexes.accessors.DatetimeProperties.week = property(lambda self: self.isocalendar().week)
