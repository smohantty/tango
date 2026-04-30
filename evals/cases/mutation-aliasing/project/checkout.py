from .promotion import apply_promotion


def finalize_checkout(cart, promo):
    """Apply the promo to the cart and return the final total."""
    apply_promotion(cart.items, promo)
    return cart.total()
