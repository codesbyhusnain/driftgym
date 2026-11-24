def hourly_hits(events):
    counts = events.set_index("ts").resample("h").size()
    return {ts.strftime("%H:%M"): int(n) for ts, n in counts.items()}
