def columns_dict(frame):
    out = {}
    for name, column in frame.iteritems():
        out[name] = column.tolist()
    return out
