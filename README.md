# ðŸš€ RKLB Stock Monitor

An automated Python tool that tracks **Rocket Lab (RKLB)** stock with live candlestick charts, technical indicators, and interactive dashboards â€” using real market data from the Alpha Vantage API.

**ðŸ”— [Try it live](https://rklb-monitor-vinhais10.streamlit.app)**

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-dashboard-red.svg)
![Status](https://img.shields.io/badge/status-live-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ðŸ“Š Screenshots

### Dashboard â€” KPIs and main chart

![Dashboard](dashboard.png)

### Full chart â€” candlesticks, RSI, and volume

![Chart](chart.png)

### Recent data table

![Table](table.png)

## ðŸ“Œ What This Does

Rocket Lab is a publicly traded space company (NASDAQ: RKLB). Tracking its price action manually is slow and error-prone. This project automates the entire process:

- Fetches real daily OHLCV data from Alpha Vantage
- Computes technical indicators (RSI, SMA, VWAP, Bollinger Bands)
- Renders an interactive dashboard with candlestick charts, RSI panel, and volume
- Optionally sends automatic Telegram alerts for RSI overbought/oversold and price moves >= 5%

## âœ¨ Features

- **Real market data** â€” daily OHLCV from the Alpha Vantage API
- **Interactive dashboard** â€” dark theme with KPI cards and Plotly charts
- **Candlestick chart** with 20-day and 50-day SMAs
- **Bollinger Bands** with fill between upper/lower bounds
- **RSI (14-period) panel** with overbought/oversold reference lines
- **Volume panel** synced to the price chart
- **Ticker input** â€” switch symbols directly from the sidebar
- **Lookback slider** â€” choose 30, 90, 180, or 365 days
- **Recent data table** â€” last 10 trading days with all indicators
- **Telegram bot** (optional) â€” /price, /chart, and /help commands
- **Automatic alerts** â€” RSI crosses and 5%+ daily moves
- **Unit tests** for indicator calculations
- **Graceful error handling** â€” API limits and network issues don't crash the app

## ðŸ› ï¸ Tech Stack

- **Python 3.11** â€” core language
- **pandas** â€” data manipulation
- **Plotly** â€” interactive charts
- **Streamlit** â€” dashboard UI
- **Alpha Vantage API** â€” market data source
- **python-telegram-bot** (optional) â€” Telegram integration
- **pytest** â€” unit tests

## ðŸš€ Setup

### 1. Clone this repository

    git clone https://github.com/Vinhais10/RKLB-stock-monitor.git
    cd RKLB-stock-monitor

### 2. Install dependencies

    py -m pip install -r requirements.txt

### 3. Get a free Alpha Vantage API key

Go to https://www.alphavantage.co/support/#api-key and request a free key.

### 4. Create your .env file

Copy .env.example to .env and add your key:

    API_KEY=your_alphavantage_api_key_here

### 5. Run the dashboard

    py -m streamlit run app.py

The dashboard opens at http://localhost:8501

## ðŸ“ Project Structure

    RKLB-stock-monitor/
    â”œâ”€â”€ app.py                    # Streamlit dashboard
    â”œâ”€â”€ stocks.py                 # Core logic: data + technical indicators
    â”œâ”€â”€ telegram_bot.py           # Optional Telegram bot
    â”œâ”€â”€ test_rsi_functions.py     # Unit tests for indicators
    â”œâ”€â”€ config.py                 # Local API keys (gitignored)
    â”œâ”€â”€ config_template.py        # Template for config
    â”œâ”€â”€ requirements.txt
    â”œâ”€â”€ .env.example              # Template for environment variables
    â”œâ”€â”€ .gitignore
    â””â”€â”€ README.md

## ðŸ§  Technical Indicators

### RSI (Relative Strength Index)

Measures momentum on a 0-100 scale.

- < 30 â€” Oversold (potential buy signal)
- 30-70 â€” Neutral
- > 70 â€” Overbought (potential sell signal)

### SMA (Simple Moving Average)

Two periods displayed:

- **SMA 20** (blue) â€” short-term trend
- **SMA 50** (orange) â€” medium-term trend

When SMA 20 crosses above SMA 50 = golden cross (bullish).
When SMA 20 crosses below SMA 50 = death cross (bearish).

### Bollinger Bands

20-day SMA +/- 2 standard deviations. Price near the upper band signals strength; near the lower band signals weakness.

### VWAP (Volume-Weighted Average Price)

Average price weighted by volume â€” used by traders to gauge whether price is trading above or below fair value.

## ðŸ“¤ Example Output

| Date | Open | High | Low | Close | Volume | RSI |
|---|---|---|---|---|---|---|
| 2026-09-25 | 74.15 | 75.32 | 72.78 | 73.95 | 18.9M | 67.21 |
| 2026-09-24 | 69.78 | 75.46 | 68.92 | 73.61 | 25.3M | 67.34 |
| 2026-09-23 | 72.87 | 73.57 | 70.08 | 70.31 | 19.3M | 64.04 |
| 2026-09-22 | 71.64 | 72.50 | 70.10 | 71.98 | 22.0M | 69.22 |

## ðŸ—ºï¸ Roadmap

- [x] Real OHLCV data from Alpha Vantage
- [x] Technical indicators (RSI, SMA, VWAP, Bollinger)
- [x] Candlestick chart with overlays
- [x] Telegram bot with /price, /chart, /help
- [x] Automatic RSI and price-move alerts
- [x] Unit tests for indicators
- [x] Interactive Streamlit dashboard
- [x] Deploy to Streamlit Cloud
- [ ] Multi-ticker watchlist
- [ ] Backtesting engine
- [ ] MACD indicator
- [ ] Email alerts
- [ ] Comparison with peers (AST SpaceMobile, Firefly, etc.)

## ðŸ¤ Contributing

Pull requests are welcome. For major changes, please open an issue first.

## ðŸ“„ License

This project is licensed under the MIT License.

## ðŸ™ Acknowledgements

- Alpha Vantage (https://www.alphavantage.co/) for the free market data API
- Streamlit (https://streamlit.io/) for the dashboard framework
- Plotly (https://plotly.com/) for the interactive charts

---

Built as part of a self-directed Python learning project, applying real-world data analysis to financial markets.
