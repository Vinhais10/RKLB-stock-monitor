# RKLB Stock Monitor

An automated Python tool that tracks Rocket Lab (RKLB) stock and displays a live-updating candlestick chart with moving averages and volume, using real market data from the Alpha Vantage API.

![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## Features

- Real daily OHLCV (Open, High, Low, Close, Volume) data via the Alpha Vantage API
- Candlestick chart with 20-day and 50-day moving averages
- Volume panel synced to the price chart
- Live price/change badge on the chart
- Automatic hourly refresh with terminal heartbeat logging
- Graceful error handling (API limits, network issues) without crashing

## Tech Stack

- **Python 3.14**
- **pandas** — structuring API data into a time-indexed DataFrame
- **mplfinance** — candlestick chart rendering
- **matplotlib** — chart styling and live window updates
- **requests** — HTTP calls to the Alpha Vantage API

## Setup

1. Clone this repository
2. Install dependencies:

pip install requests pandas matplotlib mplfinance

3. Get a free API key at [alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
4. Copy `config_template.py` to `config.py` and add your key:
```python
   API_KEY = "your_key_here"
```
5. Run:

python stocks.py


## How It Works

The script fetches daily price data from Alpha Vantage, structures it into a pandas DataFrame, and renders a candlestick chart with `mplfinance`. It then loops indefinitely, refreshing the data on a timer (default: hourly, respecting Alpha Vantage's free-tier 25 requests/day limit) and printing a heartbeat to the terminal so you can confirm it's still running.

## Roadmap

- [x] VWAP (Volume Weighted Average Price) indicator
- [x] RSI (Relative Strength Index)
- [x] Bollinger Bands
- [x] High-of-day / Low-of-day markers
- [x] Unit tests
- [x] Telegram bot (`/price`, `/chart`, `/help`)
- [x] Automatic alerts (RSI overbought/oversold, daily price moves ≥5%)
- [ ] 24/7 hosting — infrastructure ready on Oracle Cloud (Always Free tier: VCN, subnet, SSH key configured), pending shape capacity availability in the region
- [ ] Live terminal dashboard (via `rich`)
- [ ] Modular project structure (`src/` package)
## Note

This project uses the free tier of the Alpha Vantage API (25 requests/day, end-of-day data only). Real-time/intraday data requires a paid plan.

---

Built as part of a self-directed Python learning project — from zero to a working data-driven application.
