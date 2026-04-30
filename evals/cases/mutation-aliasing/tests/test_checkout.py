from project.cart import Cart
from project.checkout import finalize_checkout


def test_checkout_applies_discount_to_total():
    cart = Cart()
    cart.add("Widget", "tools", 100.0)

    promo = {"category": "tools", "discount": 0.10}

    final = finalize_checkout(cart, promo)

    assert final == 90.0


def test_checkout_applies_discount_to_cart_state():
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

    assert final == 85.0
