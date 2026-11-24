import pandas as pd

COLUMNS = ["ts", "page", "user", "ms"]


def load_events(records):
    events = pd.DataFrame(list(records), columns=COLUMNS)
    events["ts"] = pd.to_datetime(events["ts"])
    events["ms"] = events["ms"].astype(int)
    return normalise(events)


def normalise(events):
    out = events.copy()
    for column in out.columns:
        if out[column].dtype == object:
            out[column] = out[column].str.strip().str.lower()
    return out
