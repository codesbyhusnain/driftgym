def top_categories(products, n=3):
    counts = products["category"].value_counts().rename_axis("category").reset_index(name="count")
    return counts.head(n)


def category_share(products):
    shares = products["category"].value_counts(normalize=True)
    return {category: round(float(share), 3) for category, share in shares.items()}
