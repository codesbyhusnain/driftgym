def latency_rows(table):
    formatted = table[["ms"]].map(lambda v: f"{v:,} ms")
    return table.assign(ms=formatted["ms"]).values.tolist()
