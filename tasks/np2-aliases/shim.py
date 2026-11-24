import numpy as _np

_np.asfarray = lambda a, dtype=_np.float64: _np.asarray(a, dtype=dtype)
_np.round_ = _np.round
_np.cumproduct = _np.cumprod
_np.product = _np.prod
_np.float_ = _np.float64
_np.NaN = _np.nan
_np.alltrue = _np.all
