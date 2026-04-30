from project.audit import hypothetical_total_with_promo
from project.cart import Cart


def test_audit_does_not_mutate_cart():
    cart = Cart()
    cart.add("Widget", "tools", 100.0)
    cart.add("Sprocket", "tools", 50.0)
    cart.add("Apple", "food", 2.0)

    promo = {"category": "tools", "discount": 0.10}

    original_total = cart.total()
    hypothetical = hypothetical_total_with_promo(cart, promo)

    # The hypothetical should be 100*0.9 + 50*0.9 + 2 = 137.0
    assert hypothetical == 137.0, f"Hypothetical total wrong: {hypothetical}"
    # And the cart MUST be unchanged.
    assert cart.total() == original_total, (
        f"Audit mutated the cart! Was {original_total}, now {cart.total()}"
    )
    assert cart.items[0]["price"] == 100.0
    assert cart.items[1]["price"] == 50.0


def test_repeated_audits_are_independent():
    cart = Cart()
    cart.add("Hammer", "tools", 20.0)

    promo = {"category": "tools", "discount": 0.50}

    first = hypothetical_total_with_promo(cart, promo)
    second = hypothetical_total_with_promo(cart, promo)

    assert first == second, (
        f"Repeated audit returned different totals ({first} vs {second}); "
        f"cart state is leaking between audits"
    )
