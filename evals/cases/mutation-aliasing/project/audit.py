from .promotion import apply_promotion


def hypothetical_total_with_promo(cart, promo):
    """Read-only: return what the cart total WOULD be if this promo were applied.

    Must not modify the cart.
    """
    items = cart.get_items()
    apply_promotion(items, promo)
    return round(sum(item["price"] for item in items), 2)
