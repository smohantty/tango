def apply_promotion(items, promo):
    """Apply a category-targeted percentage discount to items.

    Mutates items in place and returns them.
    """
    for item in items:
        if item["category"] == promo["category"]:
            item["price"] = round(item["price"] * (1 - promo["discount"]), 2)
    return items
