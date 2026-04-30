# Ground truth: mutation-aliasing

## Root cause

Two interacting facts:

1. `project/promotion.py:apply_promotion` mutates its `items`
   argument in place (it also returns the list, but mutation is the
   primary contract that callers rely on).
2. `project/cart.py:Cart.get_items` returns the live `self.items`
   list, not a copy.

`audit.hypothetical_total_with_promo` calls `cart.get_items()` (which
hands out a live reference), then `apply_promotion(items, promo)`
(which mutates in place) — so the live cart gets mutated through the
shared reference.

`checkout.finalize_checkout` is the second caller of `apply_promotion`
and it **depends** on the in-place mutation: it discards the return
value and reads `cart.total()` directly afterwards. Any fix that
changes `apply_promotion`'s mutation contract MUST also update
`checkout.py`.

## Acceptable fixes

1. **Audit copies before mutating** (preferred — smallest, most
   targeted; respects the existing checkout contract):
   ```python
   import copy
   def hypothetical_total_with_promo(cart, promo):
       items = copy.deepcopy(cart.get_items())
       apply_promotion(items, promo)
       return round(sum(item["price"] for item in items), 2)
   ```
2. **`Cart.get_items` returns a deep copy.** Defensible — better
   encapsulation. But broader blast radius (every caller of
   `get_items` now gets a copy); requires checking all callers.
3. **Make `apply_promotion` non-mutating AND update `checkout.py`**
   in the same change to assign the return value back:
   ```python
   def finalize_checkout(cart, promo):
       cart.items = apply_promotion(cart.items, promo)
       return cart.total()
   ```
   Acceptable, but largest scope. Both call sites must change
   together or checkout silently breaks.

## Unacceptable fixes (the trap)

- **Make `apply_promotion` non-mutating without updating
  `checkout.py`.** Symptom test passes; regression tests fail
  (checkout returns the original total because it discards the
  return value).
- **Shallow-copy the list in `get_items()` (`return self.items[:]`
  or `return list(self.items)`).** The list elements are dicts;
  `apply_promotion` mutates the dicts themselves, so a shallow copy
  doesn't protect the cart. Symptom test still fails.
- **Skip the promotion in audit** (e.g., reimplement the math inline
  without calling `apply_promotion`). Defeats reuse and drifts.

## Files the plan's "Root cause" section should reference

At least one of:
- `project/audit.py`
- `project/cart.py`
- `project/promotion.py`

Bonus signal: the plan explicitly names `project/checkout.py` as an
adjacent caller whose contract constrains the fix.

## Expected Codex behavior

- **Plan review (§3):** if the plan is "make `apply_promotion`
  non-mutating", Codex should ask "are all callers updated?" and
  flag `checkout.py` as an unaudited caller — P1.
- **Code review (§6):** if the diff changes `apply_promotion` to
  return a new list without touching `checkout.py`, Codex should
  flag P0 ("`finalize_checkout` discards the new return value;
  cart total will not reflect the discount"). The diff-review
  step should also catch shallow-copy fixes that leave the symptom
  test failing.
