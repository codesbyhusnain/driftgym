import pandas as pd
from pandas.api.types import is_string_dtype

COLUMNS = ["ts", "page", "user", "ms"]


def load_events(records):
    events = pd.DataFrame(list(records), columns=COLUMNS)
    events["ts"] = pd.to_datetime(events["ts"])
    events["ms"] = events["ms"].astype(int)
    return normalise(events)


def normalise(events):
    out = events.copy()
    for column in out.columns:
        if is_string_dtype(out[column]):
            out[column] = out[column].str.strip().str.lower()
    return out
