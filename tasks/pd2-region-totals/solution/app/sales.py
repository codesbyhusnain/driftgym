COLUMNS = ["units", "revenue"]


def region_totals(sales):
    return sales.groupby("region")[COLUMNS].sum().sort_index()


def region_averages(sales):
    return sales.groupby("region")[COLUMNS].mean().round(2).sort_index()
