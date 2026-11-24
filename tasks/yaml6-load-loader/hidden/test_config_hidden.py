from app.config import dump_config, load_config, load_profiles

DEFAULTS = {"host": "localhost", "port": 8000, "debug": False, "workers": 1}


def test_empty_documents_give_defaults():
    assert load_config("") == DEFAULTS
    assert load_config("# only a comment\n") == DEFAULTS


def test_yaml_types():
    text = "host: db.internal\ndebug: off\nworkers: 8\nreplicas: [a, b]\nlimits:\n  cpu: 2\nnote: ~\n"
    assert load_config(text) == {
        "host": "db.internal",
        "port": 8000,
        "debug": False,
        "workers": 8,
        "replicas": ["a", "b"],
        "limits": {"cpu": 2},
        "note": None,
    }


def test_profiles_skip_empty_documents():
    text = "---\nprofile: test\nport: 9001\n---\n---\nprofile: ci\ndebug: on\n"
    assert load_profiles(text) == {
        "test": {"host": "localhost", "port": 9001, "debug": False, "workers": 1},
        "ci": {"host": "localhost", "port": 8000, "debug": True, "workers": 1},
    }


def test_dump_round_trip():
    config = load_config("workers: 2\nhost: example.org\n")
    text = dump_config(config)
    assert text == "debug: false\nhost: example.org\nport: 8000\nworkers: 2\n"
    assert load_config(text) == config
