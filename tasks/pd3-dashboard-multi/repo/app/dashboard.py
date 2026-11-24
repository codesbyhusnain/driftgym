from app.events import load_events
from app.fmt import latency_rows
from app.pages import flag_slow, slowest_per_page
from app.traffic import hourly_hits


def build_dashboard(records, slow_ms=1000):
    events = load_events(records)
    return {
        "pages": sorted(events["page"].unique().tolist()),
        "hits_per_hour": hourly_hits(events),
        "slow_events": int(flag_slow(events, slow_ms)["slow"].sum()),
        "slowest": latency_rows(slowest_per_page(events)),
    }
