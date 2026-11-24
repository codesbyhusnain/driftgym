from pandas.api.types import is_string_dtype


def text_columns(frame):
    return [column for column in frame.columns if is_string_dtype(frame[column])]


def normalise_text(frame):
    out = frame.copy()
    for column in text_columns(out):
        out[column] = out[column].str.strip().str.lower()
    return out
