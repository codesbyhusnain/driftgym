def top_categories(products, n=3):
    counts = products["category"].value_counts().reset_index()
    counts = counts.rename(columns={"index": "category", "category": "count"})
    return counts.head(n)


def category_share(products):
    shares = products["category"].value_counts(normalize=True).reset_index()
    return {row["index"]: round(row["category"], 3) for _, row in shares.iterrows()}
