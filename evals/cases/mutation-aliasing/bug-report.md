# Bug report

The audit team is reporting that running a "what would the total be
with this promo applied" report on a cart actually changes the cart's
prices. The audit is supposed to be read-only — it must not modify the
cart it's auditing.

## Reproducer

```python
from project.cart import Cart
from project.audit import hypothetical_total_with_promo

cart = Cart()
cart.add("Widget", "tools", 100.0)
print(cart.total())                                      # 100.0
hypothetical_total_with_promo(cart, {"category": "tools", "discount": 0.10})
print(cart.total())                                      # 90.0  ← cart was mutated!
```

## Tests

- `tests/symptom/` — currently failing tests demonstrating the bug.
- `tests/regression/` — tests that should keep passing after the fix.
  Don't break them.

Please investigate and fix end-to-end with `/tango-bug`.
