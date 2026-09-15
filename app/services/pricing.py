"""Money helpers.

Prices are stored as integer cents throughout the portal to avoid the rounding
problems that come with floating point currency math. These helpers convert
between the user-facing dollar strings and the internal cents representation.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MAX_PRICE_CENTS = 100_000_000


def normalize_price(raw):
    """Parse a user-entered price string into integer cents.

    Accepts values like "12", "12.5", "$12.50". Returns None for invalid input
    and rejects values that exceed the supported price range.
    """
    if raw is None:
        return None
    cleaned = str(raw).strip().lstrip("$").replace(",", "")
    if not cleaned:
        return None
    if cleaned.lower() in {"nan", "inf", "-inf", "+inf"}:
        return None
    try:
        dollars = Decimal(cleaned)
    except InvalidOperation:
        return None
    if not dollars.is_finite():
        return None
    if dollars < 0:
        dollars = Decimal(0)
    cents = (dollars * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if cents < 0 or cents > MAX_PRICE_CENTS:
        return None
    return int(cents)


def format_price(cents):
    """Render integer cents as a dollar string, e.g. 1250 -> "$12.50"."""
    try:
        value = Decimal(int(cents)) / 100
    except (TypeError, ValueError, InvalidOperation):
        value = Decimal(0)
    return "${:.2f}".format(value)


def order_total(items):
    """Sum a list of {"price_cents", "quantity"} line items."""
    total = 0
    for item in items:
        price = int(item.get("price_cents", 0))
        quantity = int(item.get("quantity", 1))
        if quantity < 0:
            quantity = 0
        total += price * quantity
    return total
