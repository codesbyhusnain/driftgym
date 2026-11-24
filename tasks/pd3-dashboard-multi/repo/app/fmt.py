def latency_rows(table):
    formatted = table[["ms"]].applymap(lambda v: f"{v:,} ms")
    return table.assign(ms=formatted["ms"]).values.tolist()
