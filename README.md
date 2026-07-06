Simplified Trading Bot — Binance Futures Testnet (USDT-M)
A small, structured Python CLI application for placing Market, Limit, and Stop-Limit orders on the Binance USDT-M Futures Testnet, with input validation, logging, and error handling.
Project Structure
trading_bot/
bot/
init.py
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
1. Setup
1.1 Create a Binance Futures Demo Trading account
Note: Binance retired the old standalone Futures Testnet website (testnet.binancefuture.com) in August 2025. Futures testing is now done through Demo Trading (demo.binance.com), using a regular Binance account. The REST API base URL also changed to https://demo-fapi.binance.com.
Log in to your regular Binance account, then go to https://demo.binance.com and click "Start demo trading".
Click your account icon (top right) then Demo Trading API.
Choose System generated (HMAC) key type, then Next.
Give it a label (e.g. trading_bot) and confirm via email/2FA if asked.
Copy the API Key and Secret Key immediately, the secret is only shown once.
Demo Trading gives you a virtual USDT balance to trade with, no real funds are involved.
1.2 Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
1.3 Configure API credentials
Copy the example env file and fill in your testnet keys:
cp .env.example .env
Edit .env:
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
2. Running the Bot
Market order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
Limit order
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 65000
Stop-Limit order (bonus feature)
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 64000 --stop-price 64200
Each run prints an order request summary, the order response (orderId, status, executedQty, avgPrice), and a success/failure message. All requests, responses, and errors are also written to logs/trading_bot.log.
3. Error Handling
The bot handles invalid input, API errors, and network failures gracefully, printing a clear FAILED message and logging the details instead of crashing.
4. Assumptions
Only USDT-M Futures Demo Trading is targeted (base URL https://demo-fapi.binance.com). Symbols are validated against a simple pattern ending in USDT. LIMIT and STOP_LIMIT orders default to GTC time-in-force. The Stop-Limit order type was implemented as the bonus feature. API credentials are read from environment variables via a .env file.
5. Log Files
Sample log entries are written to logs/trading_bot.log. Submit the log file produced by actually running the two commands above against your own testnet credentials.
6. Bonus Implemented
Third order type: Stop-Limit. The CLI validates and reports clear error messages for every invalid input case.
