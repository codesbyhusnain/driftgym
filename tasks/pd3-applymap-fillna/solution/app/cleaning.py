def format_table(frame):
    return frame.map(lambda v: f"{v:,.2f}")


def fill_forward(readings):
    return readings.ffill()


def fill_back(readings, limit):
    return readings.bfill(limit=limit)
