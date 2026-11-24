def columns_dict(frame):
    out = {}
    for name, column in frame.items():
        out[name] = column.tolist()
    return out
