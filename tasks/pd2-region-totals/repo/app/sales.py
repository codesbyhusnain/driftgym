def region_totals(sales):
    return sales.groupby("region").sum().sort_index()


def region_averages(sales):
    return sales.groupby("region").mean().round(2).sort_index()
