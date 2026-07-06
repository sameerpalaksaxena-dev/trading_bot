"""
Command-line interface for the simplified Binance Futures Testnet trading bot.

Examples
--------
Market order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

Limit order:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000

Stop-limit order (bonus):
    python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 \\
        --price 64000 --stop-price 64200
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClientError, FuturesTestnetClient
from bot.logging_config import setup_logger
from bot.orders import place_order

logger = setup_logger()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market / Limit / Stop-Limit orders on Binance Futures Testnet (USDT-M).",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"],
                         help="Order side")
    parser.add_argument("--type", dest="order_type", required=True,
                         choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
                         help="Order type")
    parser.add_argument("--quantity", required=True, type=float, help="Order quantity")
    parser.add_argument("--price", type=float, default=None,
                         help="Order price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price", type=float, default=None,
                         help="Stop trigger price (required for STOP_LIMIT)")
    return parser


def print_summary(request: dict) -> None:
    print("\n--- Order Request Summary ---")
    for key, value in request.items():
        if value is not None:
            print(f"  {key:12s}: {value}")
    print("------------------------------")


def print_response(response: dict) -> None:
    print("\n--- Order Response ---")
    print(f"  orderId      : {response.get('orderId')}")
    print(f"  status       : {response.get('status')}")
    print(f"  executedQty  : {response.get('executedQty')}")
    print(f"  avgPrice     : {response.get('avgPrice', 'N/A')}")
    print("-----------------------")


def main():
    load_dotenv()  # load BINANCE_API_KEY / BINANCE_API_SECRET from .env if present

    parser = build_parser()
    args = parser.parse_args()

    print_summary({
        "symbol": args.symbol,
        "side": args.side,
        "order_type": args.order_type,
        "quantity": args.quantity,
        "price": args.price,
        "stop_price": args.stop_price,
    })

    api_key = os.environ.get("BINANCE_API_KEY")
    api_secret = os.environ.get("BINANCE_API_SECRET")

    try:
        client = FuturesTestnetClient(api_key, api_secret)
    except BinanceClientError as e:
        logger.error("Failed to initialize client: %s", e)
        print(f"\n[FAILED] {e}")
        sys.exit(1)

    result = place_order(
        client,
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        price=args.price,
        stop_price=args.stop_price,
    )

    if result["success"]:
        print_response(result["response"])
        print("\n[SUCCESS] Order placed successfully.")
        sys.exit(0)
    else:
        print(f"\n[FAILED] {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
