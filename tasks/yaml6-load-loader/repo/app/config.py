import yaml

DEFAULTS = {"host": "localhost", "port": 8000, "debug": False, "workers": 1}


def load_config(text):
    data = yaml.load(text) or {}
    return {**DEFAULTS, **data}


def load_profiles(text):
    profiles = {}
    for doc in yaml.load_all(text):
        if not doc:
            continue
        doc = dict(doc)
        name = doc.pop("profile")
        profiles[name] = {**DEFAULTS, **doc}
    return profiles


def dump_config(config):
    return yaml.dump(config, sort_keys=True, default_flow_style=False)
