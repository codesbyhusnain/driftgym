import pandas as pd

from app.dashboard import build_dashboard
from app.events import load_events
from app.pages import flag_slow, slowest_per_page
from app.traffic import hourly_hits


def _records():
    return [
        {"ts": "2025-02-10 08:10", "page": "Docs", "user": " Kay", "ms": 12345},
        {"ts": "2025-02-10 08:20", "page": " docs", "user": "LEE", "ms": 800},
        {"ts": "2025-02-10 10:30", "page": "Login", "user": "kay ", "ms": 1000},
        {"ts": "2025-02-10 10:45", "page": "login", "user": "Mo", "ms": 1001},
    ]


def test_hour_without_events_is_zero():
    assert hourly_hits(load_events(_records())) == {"08:00": 2, "09:00": 0, "10:00": 2}


def test_flag_slow_threshold_and_input_unchanged():
    events = load_events(_records())
    before = events.copy()
    flagged = flag_slow(events, 1000)
    assert flagged["slow"].tolist() == [True, False, False, True]
    assert flagged["slow"].dtype == bool
    pd.testing.assert_frame_equal(events, before)


def test_slowest_per_page():
    table = slowest_per_page(load_events(_records()))
    assert list(table.columns) == ["page", "user", "ms"]
    assert table.values.tolist() == [["docs", "kay", 12345], ["login", "mo", 1001]]
    assert list(table.index) == [0, 1]


def test_dashboard_with_one_event_and_a_low_threshold():
    record = {"ts": "2025-02-11 23:59", "page": " Admin", "user": "Root ", "ms": 30}
    assert build_dashboard([record], slow_ms=10) == {
        "pages": ["admin"],
        "hits_per_hour": {"23:00": 1},
        "slow_events": 1,
        "slowest": [["admin", "root", "30 ms"]],
    }
