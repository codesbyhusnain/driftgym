import yaml as _yaml

_load, _load_all = _yaml.load, _yaml.load_all
_yaml.load = lambda stream, Loader=_yaml.FullLoader: _load(stream, Loader=Loader)
_yaml.load_all = lambda stream, Loader=_yaml.FullLoader: _load_all(stream, Loader=Loader)
