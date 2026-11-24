def format_table(frame):
    return frame.applymap(lambda v: f"{v:,.2f}")


def fill_forward(readings):
    return readings.fillna(method="ffill")


def fill_back(readings, limit):
    return readings.fillna(method="bfill", limit=limit)
