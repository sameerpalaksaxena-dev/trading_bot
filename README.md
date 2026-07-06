# Simplified Trading Bot — Binance Futures Testnet (USDT-M)

A small, structured Python CLI application for placing Market, Limit, and
Stop-Limit orders on the Binance USDT-M Futures Testnet, with input
validation, logging, and error handling.

## Project Structure

```
trading_bot/
  bot/
    __init__.py
    client.py           # Binance Futures Testnet client wrapper
    orders.py           # order placement logic (validation + API call)
    validators.py        # input validation
    logging_config.py    # logging setup (file + console)
  cli.py                 # CLI entry point
  logs/
    trading_bot.log      # generated at runtime
  requirements.txt
  .env.example
  README.md
```

## 1. Setup

### 1.1 Create a Binance Futures Testnet account
1. Go to https://testnet.binancefuture.com and log in with a GitHub account.
2. Once logged in, generate an **API Key** and **API Secret** from the
   testnet dashboard (top right, "API Key").
3. The testnet gives you a virtual USDT balance you can trade with —
   no real funds are involved.

### 1.2 Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1.3 Configure API credentials

Copy the example env file and fill in your testnet keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

The CLI loads these automatically via `python-dotenv`. Alternatively,
export them directly as environment variables instead of using a `.env` file.

## 2. Running the Bot

### Market order
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Limit order
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
```

### Stop-Limit order (bonus feature)
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 \
  --price 64000 --stop-price 64200
```

Each run prints:
1. An **order request summary** (what is about to be sent)
2. The **order response** (`orderId`, `status`, `executedQty`, `avgPrice`)
3. A **success/failure** message

All requests, responses, and errors are also written to `logs/trading_bot.log`.

## 3. Error Handling

The bot handles three broad categories of failure gracefully (prints a
clear `[FAILED]` message and logs the details, rather than crashing):

- **Invalid input** — e.g. missing price for a LIMIT order, negative
  quantity, malformed symbol. Caught in `bot/validators.py` before any
  network call is made.
- **API errors** — e.g. insufficient testnet balance, invalid symbol,
  rejected order. Caught via `BinanceAPIException` / `BinanceOrderException`
  in `bot/client.py`.
- **Network failures** — e.g. timeout or connection error reaching the
  testnet endpoint. Caught and re-raised as a single `BinanceClientError`
  so the CLI layer only has one exception type to handle.

## 4. Assumptions

- Only **USDT-M Futures Testnet** is targeted (base URL
  `https://testnet.binancefuture.com`), not Spot Testnet or Coin-M Futures.
- Symbols are validated against a simple pattern (uppercase alphanumeric
  ending in `USDT`, e.g. `BTCUSDT`) rather than validated live against
  Binance's exchange-info endpoint, to keep the task within scope.
- LIMIT and STOP_LIMIT orders default to `GTC` (Good-Till-Canceled) time-in-force,
  since the task didn't specify a required value.
- The **Stop-Limit** order type was implemented as the bonus feature. On
  Binance Futures this is sent as order type `STOP` with both `price` and
  `stopPrice`.
- API credentials are read from environment variables (via a `.env` file)
  rather than passed on the command line, to avoid leaking secrets into
  shell history or process lists.
- The account is assumed to already have testnet USDT balance and, for
  Futures, an open position mode compatible with one-way orders (Binance
  Futures Testnet accounts default to one-way mode).

## 5. Log Files

Sample log entries are written to `logs/trading_bot.log`. Because this file
is generated per-run against a live (test) exchange connection, submit the
log file produced by actually running the two commands above against your
own testnet credentials — it will contain the real request, the real
response (with `orderId`, `status`, `executedQty`), and a timestamp,
satisfying the "log files from at least one MARKET and one LIMIT order"
deliverable.

## 6. Bonus Implemented

- ✅ Third order type: **Stop-Limit**
- The CLI validates and reports clear, specific error messages for every
  invalid input case (missing price, bad symbol, non-numeric quantity, etc.)
