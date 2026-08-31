# RKLB Stock Monitor

An automated Python tool that tracks Rocket Lab (RKLB) stock: renders technical charts (candlesticks, moving averages, VWAP, Bollinger Bands, RSI, volume), and sends live alerts to Telegram — using real market data from the Alpha Vantage API.

![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

![RKLB Chart](<img width="800" height="575" alt="RKLB CHART" src="https://github.com/user-attachments/assets/21be432c-d3ae-4fc8-aaf2-9df54cde5c2c" />
)

## Features

- Real daily OHLCV (Open, High, Low, Close, Volume) data via the Alpha Vantage API
- Candlestick chart with 20-day and 50-day moving averages, VWAP, and Bollinger Bands
- RSI (14-period) panel with overbought/oversold reference lines
- High-of-day / Low-of-day markers
- Volume panel synced to the price chart
- Telegram bot with `/price`, `/chart`, and `/help` commands
- Automatic alerts (RSI overbought/oversold, daily price moves ≥5%) sent straight to Telegram
- Unit tests for all technical indicator calculations
- Graceful error handling (API limits, network issues, unknown commands) without crashing

## Tech Stack

- **Python 3.14**
- **pandas** — structuring API data into a time-indexed DataFrame
- **mplfinance** — candlestick chart rendering
- **matplotlib** — chart styling and live window updates
- **requests** — HTTP calls to the Alpha Vantage API
- **python-telegram-bot** — Telegram bot commands and scheduled alert checks

## Setup

1. Clone this repository
2. Install dependencies:
