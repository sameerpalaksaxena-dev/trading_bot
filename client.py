"""
Thin wrapper around the python-binance Client, configured to talk to the
Binance Futures (USDT-M) Testnet.

This isolates all direct SDK/API usage from the rest of the app so the
CLI and order logic never touch python-binance directly.
"""

import logging

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException, BinanceRequestException

logger = logging.getLogger("trading_bot")

FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


class BinanceClientError(Exception):
    """Raised when the underlying Binance client fails in a way the caller must handle."""


class FuturesTestnetClient:
    """
    Wraps python-binance's Client for USDT-M Futures Testnet trading.

    Usage:
        client = FuturesTestnetClient(api_key, api_secret)
        response = client.create_order(symbol="BTCUSDT", side="BUY",
                                        order_type="MARKET", quantity=0.01)
    """

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise BinanceClientError(
                "API key/secret not found. Set BINANCE_API_KEY and "
                "BINANCE_API_SECRET as environment variables."
            )

        # python-binance's `testnet=True` flag points spot endpoints at
        # testnet, but for Futures we must explicitly override FUTURES_URL
        # to hit the Futures Testnet base URL rather than production.
        self._client = Client(api_key, api_secret, testnet=True)
        self._client.FUTURES_URL = FUTURES_TESTNET_BASE_URL + "/fapi"

        logger.info("Initialized Binance Futures Testnet client (base_url=%s)", FUTURES_TESTNET_BASE_URL)

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        stop_price: float = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """
        Submit an order to Binance Futures Testnet.

        Args:
            symbol: e.g. "BTCUSDT"
            side: "BUY" or "SELL"
            order_type: "MARKET", "LIMIT", or "STOP_LIMIT" (mapped to STOP for futures)
            quantity: order quantity
            price: required for LIMIT / STOP_LIMIT
            stop_price: required for STOP_LIMIT
            time_in_force: defaults to "GTC" (Good Till Canceled), used for LIMIT orders

        Returns:
            The raw order response dict from Binance.

        Raises:
            BinanceClientError: wraps network, API, and order-specific errors.
        """
        params = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
        }

        if order_type == "MARKET":
            params["type"] = "MARKET"
        elif order_type == "LIMIT":
            params["type"] = "LIMIT"
            params["price"] = price
            params["timeInForce"] = time_in_force
        elif order_type == "STOP_LIMIT":
            # Binance Futures uses "STOP" as the order type for a stop-limit order
            params["type"] = "STOP"
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = time_in_force
        else:
            raise BinanceClientError(f"Unsupported order type: {order_type}")

        logger.info("Sending order request: %s", params)

        try:
            response = self._client.futures_create_order(**params)
            logger.info("Order response: %s", response)
            return response

        except BinanceOrderException as e:
            logger.error("Order rejected by Binance: %s", e)
            raise BinanceClientError(f"Order rejected: {e}") from e

        except BinanceAPIException as e:
            logger.error("Binance API error (code=%s): %s", getattr(e, "code", "?"), e)
            raise BinanceClientError(f"API error: {e}") from e

        except BinanceRequestException as e:
            logger.error("Malformed request to Binance: %s", e)
            raise BinanceClientError(f"Request error: {e}") from e

        except (ConnectionError, TimeoutError) as e:
            logger.error("Network failure while contacting Binance: %s", e)
            raise BinanceClientError(f"Network error: {e}") from e

        except Exception as e:  # noqa: BLE001 - final safety net, logged and re-raised as our own type
            logger.error("Unexpected error while placing order: %s", e)
            raise BinanceClientError(f"Unexpected error: {e}") from e

    def get_account_balance(self) -> list:
        """Fetch USDT-M futures account balances (useful for sanity checks)."""
        try:
            balances = self._client.futures_account_balance()
            logger.info("Fetched account balance successfully.")
            return balances
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to fetch account balance: %s", e)
            raise BinanceClientError(f"Failed to fetch balance: {e}") from e
