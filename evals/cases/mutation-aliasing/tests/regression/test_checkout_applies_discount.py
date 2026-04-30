"""Regression tests: must pass before AND after the fix.

These guard against fixes that make `apply_promotion` non-mutating
without updating `checkout.py` to use its return value. Such a fix
silently breaks checkout — the discount return value is discarded
and the cart total stays at the original price.
"""
from project.cart import Cart
from project.checkout import finalize_checkout


def test_checkout_applies_discount_to_total():
    cart = Cart()
    cart.add("Widget", "tools", 100.0)

    promo = {"category": "tools", "discount": 0.10}

    final = finalize_checkout(cart, promo)

    assert final == 90.0, f"Expected discounted total $90.00, got ${final}"


def test_checkout_applies_discount_to_cart_state():
    """After checkout, the cart's items reflect the discount.

    Downstream code (receipts, refunds) reads cart.items directly.
    """
    cart = Cart()
    cart.add("Widget", "tools", 100.0)
    cart.add("Apple", "food", 2.0)

    promo = {"category": "tools", "discount": 0.10}

    finalize_checkout(cart, promo)

    assert cart.items[0]["price"] == 90.0
    assert cart.items[1]["price"] == 2.0


def test_checkout_handles_multiple_categories():
    cart = Cart()
    cart.add("Hammer", "tools", 30.0)
    cart.add("Saw", "tools", 70.0)
    cart.add("Bread", "food", 5.0)

    promo = {"category": "tools", "discount": 0.20}

    final = finalize_checkout(cart, promo)

    # 30*0.8 + 70*0.8 + 5 = 24 + 56 + 5 = 85.0
    assert final == 85.0, f"Expected $85.00, got ${final}"
