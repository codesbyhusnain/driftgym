from app.config import load_config, load_profiles


def test_load_config():
    assert load_config("port: 8080\ndebug: yes\n") == {"host": "localhost", "port": 8000, "debug": True, "workers": 1}


def test_load_profiles():
    text = "profile: dev\ndebug: true\n---\nprofile: prod\nworkers: 4\n"
    assert load_profiles(text) == {
        "dev": {"host": "localhost", "port": 8000, "debug": True, "workers": 1},
        "prod": {"host": "localhost", "port": 8000, "debug": False, "workers": 4},
    }
