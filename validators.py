"""
Input validation for order requests.

Keeping validation isolated from the CLI and API layers makes it easy to
unit test and reuse (e.g. if a web UI is added later).
"""

import re

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_LIMIT"}

# Basic sanity pattern for a USDT-M perpetual futures symbol, e.g. BTCUSDT
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{2,15}USDT$")


class ValidationError(ValueError):
    """Raised when user-supplied order input fails validation."""


def validate_symbol(symbol: str) -> str:
    """Normalize and validate a trading symbol like 'btcusdt' -> 'BTCUSDT'."""
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol is required.")

    normalized = symbol.strip().upper()

    if not SYMBOL_PATTERN.match(normalized):
        raise ValidationError(
            f"Invalid symbol '{symbol}'. Expected a USDT-M pair like 'BTCUSDT'."
        )

    return normalized


def validate_side(side: str) -> str:
    """Validate order side is BUY or SELL."""
    if not side or not isinstance(side, str):
        raise ValidationError("Side is required.")

    normalized = side.strip().upper()

    if normalized not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{side}'. Must be one of {sorted(VALID_SIDES)}.")

    return normalized


def validate_order_type(order_type: str) -> str:
    """Validate order type is one of the supported types."""
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type is required.")

    normalized = order_type.strip().upper()

    if normalized not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_type}'. Must be one of {sorted(VALID_ORDER_TYPES)}."
        )

    return normalized


def validate_quantity(quantity) -> float:
    """Validate quantity is a positive number."""
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be a number, got '{quantity}'.")

    if qty <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    return qty


def validate_price(price, order_type: str):
    """
    Validate price for order types that require it (LIMIT, STOP_LIMIT).
    MARKET orders should pass price=None.
    """
    if order_type == "MARKET":
        return None

    if price is None:
        raise ValidationError(f"Price is required for {order_type} orders.")

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Price must be a number, got '{price}'.")

    if p <= 0:
        raise ValidationError("Price must be greater than zero.")

    return p


def validate_stop_price(stop_price, order_type: str):
    """Validate stop price, required only for STOP_LIMIT orders."""
    if order_type != "STOP_LIMIT":
        return None

    if stop_price is None:
        raise ValidationError("Stop price is required for STOP_LIMIT orders.")

    try:
        sp = float(stop_price)
    except (TypeError, ValueError):
        raise ValidationError(f"Stop price must be a number, got '{stop_price}'.")

    if sp <= 0:
        raise ValidationError("Stop price must be greater than zero.")

    return sp


def validate_order_request(symbol, side, order_type, quantity, price=None, stop_price=None):
    """
    Run all validations for a single order request and return a clean dict.
    Raises ValidationError on the first failure encountered.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)
    clean_stop_price = validate_stop_price(stop_price, clean_type)

    return {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_type,
        "quantity": clean_qty,
        "price": clean_price,
        "stop_price": clean_stop_price,
    }
