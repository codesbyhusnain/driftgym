def slowest_per_page(events):
    ranked = events.sort_values(["page", "ms"], ascending=[True, False])
    return ranked.groupby("page").head(1).reset_index(drop=True)[["page", "user", "ms"]]


def flag_slow(events, threshold_ms):
    out = events.copy()
    out["slow"] = out["ms"] > threshold_ms
    return out
