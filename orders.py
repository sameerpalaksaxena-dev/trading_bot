"""
Order placement logic: ties validation + the API client together and
formats a consistent result for the CLI to print.
"""

import logging

from bot.client import BinanceClientError, FuturesTestnetClient
from bot.validators import ValidationError, validate_order_request

logger = logging.getLogger("trading_bot")


def place_order(client: FuturesTestnetClient, symbol, side, order_type, quantity,
                 price=None, stop_price=None) -> dict:
    """
    Validate input, submit the order, and return a normalized result dict.

    Returns:
        {
            "success": bool,
            "request": {...},        # the validated request that was sent
            "response": {...} | None,  # raw Binance response if successful
            "error": str | None,     # error message if unsuccessful
        }
    """
    # Step 1: validate input before ever touching the network
    try:
        clean = validate_order_request(symbol, side, order_type, quantity, price, stop_price)
    except ValidationError as e:
        logger.warning("Validation failed for order request: %s", e)
        return {
            "success": False,
            "request": {
                "symbol": symbol, "side": side, "order_type": order_type,
                "quantity": quantity, "price": price, "stop_price": stop_price,
            },
            "response": None,
            "error": str(e),
        }

    logger.info(
        "Placing %s %s order: symbol=%s qty=%s price=%s stop_price=%s",
        clean["order_type"], clean["side"], clean["symbol"],
        clean["quantity"], clean["price"], clean["stop_price"],
    )

    # Step 2: submit to Binance Futures Testnet
    try:
        response = client.create_order(
            symbol=clean["symbol"],
            side=clean["side"],
            order_type=clean["order_type"],
            quantity=clean["quantity"],
            price=clean["price"],
            stop_price=clean["stop_price"],
        )
        return {
            "success": True,
            "request": clean,
            "response": response,
            "error": None,
        }

    except BinanceClientError as e:
        logger.error("Order failed: %s", e)
        return {
            "success": False,
            "request": clean,
            "response": None,
            "error": str(e),
        }
