import networkx as _nx
import numpy as _np

_nx.to_numpy_matrix = lambda graph, **kwargs: _np.asmatrix(_nx.to_numpy_array(graph, **kwargs))
_nx.from_numpy_matrix = lambda matrix, **kwargs: _nx.from_numpy_array(_np.asarray(matrix), **kwargs)
_nx.info = str
