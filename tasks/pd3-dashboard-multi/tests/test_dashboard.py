from app.dashboard import build_dashboard
from app.events import load_events
from app.traffic import hourly_hits

RECORDS = [
    {"ts": "2024-06-01 09:05", "page": " Home ", "user": "U1", "ms": 120},
    {"ts": "2024-06-01 09:40", "page": "Search", "user": "U2", "ms": 1500},
    {"ts": "2024-06-01 10:10", "page": "home", "user": "U3", "ms": 2300},
    {"ts": "2024-06-01 11:55", "page": "SEARCH ", "user": "u1", "ms": 900},
    {"ts": "2024-06-01 11:59", "page": "Cart", "user": "U2", "ms": 450},
]


def test_load_events_normalises_text():
    events = load_events(RECORDS)
    assert events["page"].tolist() == ["home", "search", "home", "search", "cart"]
    assert events["user"].tolist() == ["u1", "u2", "u3", "u1", "u2"]


def test_hourly_hits():
    assert hourly_hits(load_events(RECORDS)) == {"09:00": 2, "10:00": 1, "11:00": 2}


def test_build_dashboard():
    assert build_dashboard(RECORDS) == {
        "pages": ["cart", "home", "search"],
        "hits_per_hour": {"09:00": 2, "10:00": 1, "11:00": 2},
        "slow_events": 2,
        "slowest": [["cart", "u2", "450 ms"], ["home", "u3", "2,300 ms"], ["search", "u2", "1,500 ms"]],
    }
