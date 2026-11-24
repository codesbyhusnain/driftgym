def slowest_per_page(events):
    rows = events.groupby("page").apply(lambda g: g.nlargest(1, "ms"))
    return rows.reset_index(drop=True)[["page", "user", "ms"]]


def flag_slow(events, threshold_ms):
    out = events.copy()
    out["slow"] = False
    out["slow"][out["ms"] > threshold_ms] = True
    return out
