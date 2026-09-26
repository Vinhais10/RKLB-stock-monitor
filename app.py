"""
RKLB Stock Monitor - Streamlit dashboard.

Reuses the technical indicator logic from stocks.py,
presented as an interactive web dashboard.
"""

import os
from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import requests

st.set_page_config(
    page_title="RKLB Stock Monitor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# DESIGN SYSTEM
# ============================================================
COLORS = {
    "primary": "#6366F1",
    "success": "#10B981",
    "danger":  "#EF4444",
    "warning": "#F59E0B",
    "text":    "#F1F5F9",
    "muted":   "#94A3B8",
    "up":      "#26a69a",
    "down":    "#ef5350",
}

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .kpi-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
    }
    .kpi-label {
        color: #94A3B8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #F1F5F9;
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.1;
    }
    .kpi-sub {
        color: #94A3B8;
        font-size: 0.8rem;
        margin-top: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API KEY LOADER (env local OR Streamlit secrets)
# ============================================================
def get_api_key():
    key = os.environ.get("API_KEY")
    if key:
        return key
    try:
        return st.secrets["API_KEY"]
    except Exception:
        return None


# ============================================================
# DATA + INDICATORS (adapted from stocks.py)
# ============================================================
@st.cache_data(ttl=3600)
def load_data(symbol: str, api_key: str):
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    )
    r = requests.get(url, timeout=15)
    data = r.json()

    if "Error Message" in data or "Time Series (Daily)" not in data:
        return None, data.get("Note") or data.get("Information") or "Unknown API error"

    rows = []
    for day, e in data["Time Series (Daily)"].items():
        rows.append({
            "Date":   pd.to_datetime(day),
            "Open":   float(e["1. open"]),
            "High":   float(e["2. high"]),
            "Low":    float(e["3. low"]),
            "Close":  float(e["4. close"]),
            "Volume": float(e["5. volume"]),
        })

    df = pd.DataFrame(rows).set_index("Date").sort_index()
    return df, None


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # RSI (14)
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))

    # SMA
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()

    # Bollinger Bands
    mid = df["Close"].rolling(20).mean()
    std = df["Close"].rolling(20).std()
    df["BB_upper"] = mid + 2 * std
    df["BB_lower"] = mid - 2 * std

    # VWAP (cumulative)
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (tp * df["Volume"]).cumsum() / df["Volume"].cumsum()

    return df


def rsi_label(v):
    if pd.isna(v):
        return "—"
    if v < 30:
        return "OVERSOLD"
    if v > 70:
        return "OVERBOUGHT"
    return "NEUTRAL"


# ============================================================
# HEADER
# ============================================================
st.title("🚀 RKLB Stock Monitor")
st.caption("Live technical dashboard for Rocket Lab (RKLB) — data from Alpha Vantage.")


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    symbol = st.text_input("Ticker symbol", value="RKLB").upper().strip()

    lookback = st.slider(
        "Days to display",
        min_value=30, max_value=365, value=90, step=30,
    )

    st.divider()
    st.caption("**Powered by** Alpha Vantage API")
    st.caption(f"Data cached for 1 hour.")


# ============================================================
# LOAD DATA
# ============================================================
api_key = get_api_key()

if not api_key:
    st.error(
        "⚠️ API key not found. Add it to `.env` locally, "
        "or to Streamlit secrets when deployed."
    )
    st.stop()

with st.spinner(f"Loading {symbol} data..."):
    df, error = load_data(symbol, api_key)

if df is None:
    st.error(f"⚠️ Could not load data: {error}")
    st.info(
        "Common reasons: API rate limit (5 calls/min on free tier), "
        "invalid symbol, or network issue."
    )
    st.stop()

df = add_indicators(df)
df = df.tail(lookback)

latest = df.iloc[-1]
prev = df.iloc[-2]

price = latest["Close"]
change = price - prev["Close"]
change_pct = (change / prev["Close"]) * 100
rsi_val = latest["RSI"]

# ============================================================
# KPI CARDS
# ============================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{symbol} price</div>
            <div class="kpi-value">${price:.2f}</div>
            <div class="kpi-sub">last close</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k2:
    color = COLORS["success"] if change >= 0 else COLORS["danger"]
    arrow = "▲" if change >= 0 else "▼"
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Daily change</div>
            <div class="kpi-value" style="color:{color};">
                {arrow} {change_pct:+.2f}%
            </div>
            <div class="kpi-sub">{change:+.2f} USD</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k3:
    rsi_color = (
        COLORS["danger"] if rsi_val > 70
        else COLORS["success"] if rsi_val < 30
        else COLORS["text"]
    )
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">RSI (14)</div>
            <div class="kpi-value" style="color:{rsi_color};">{rsi_val:.1f}</div>
            <div class="kpi-sub">{rsi_label(rsi_val)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with k4:
    vol = latest["Volume"]
    avg_vol = df["Volume"].tail(30).mean()
    vol_ratio = vol / avg_vol if avg_vol else 1.0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Volume</div>
            <div class="kpi-value">{vol/1e6:.1f}M</div>
            <div class="kpi-sub">{vol_ratio:.2f}× 30d avg</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ============================================================
# CHART: price + RSI + volume
# ============================================================
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.04,
    row_heights=[0.6, 0.2, 0.2],
    subplot_titles=("", "RSI (14)", "Volume"),
)

# --- Candlesticks ---
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"],
        name=symbol,
        increasing_line_color=COLORS["up"],
        decreasing_line_color=COLORS["down"],
    ),
    row=1, col=1,
)

# --- SMAs ---
fig.add_trace(
    go.Scatter(x=df.index, y=df["SMA20"], name="SMA 20",
               line=dict(color="#1f77b4", width=1.2)),
    row=1, col=1,
)
fig.add_trace(
    go.Scatter(x=df.index, y=df["SMA50"], name="SMA 50",
               line=dict(color="#ff7f0e", width=1.2)),
    row=1, col=1,
)

# --- Bollinger Bands ---
fig.add_trace(
    go.Scatter(x=df.index, y=df["BB_upper"], name="BB upper",
               line=dict(color="#90a4ae", width=0.8, dash="dash")),
    row=1, col=1,
)
fig.add_trace(
    go.Scatter(x=df.index, y=df["BB_lower"], name="BB lower",
               line=dict(color="#90a4ae", width=0.8, dash="dash"),
               fill="tonexty", fillcolor="rgba(144,164,174,0.1)"),
    row=1, col=1,
)

# --- RSI ---
fig.add_trace(
    go.Scatter(x=df.index, y=df["RSI"], name="RSI",
               line=dict(color="#7e57c2", width=1.5)),
    row=2, col=1,
)
fig.add_hline(y=70, line=dict(color=COLORS["danger"], width=0.8, dash="dash"),
              row=2, col=1)
fig.add_hline(y=30, line=dict(color=COLORS["success"], width=0.8, dash="dash"),
              row=2, col=1)

# --- Volume ---
vol_colors = [
    COLORS["up"] if c >= o else COLORS["down"]
    for o, c in zip(df["Open"], df["Close"])
]
fig.add_trace(
    go.Bar(x=df.index, y=df["Volume"], name="Volume",
           marker_color=vol_colors, opacity=0.6),
    row=3, col=1,
)

fig.update_layout(
    height=750,
    showlegend=True,
    xaxis_rangeslider_visible=False,
    margin=dict(l=10, r=10, t=40, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1),
)

fig.update_xaxes(gridcolor="#334155", showgrid=True)
fig.update_yaxes(gridcolor="#334155", showgrid=True)

st.plotly_chart(fig, use_container_width=True)


# ============================================================
# RECENT DATA TABLE
# ============================================================
st.divider()
st.subheader("📋 Recent data")
recent = df.tail(10).iloc[::-1][["Open", "High", "Low", "Close", "Volume", "RSI"]].round(2)
st.dataframe(recent, use_container_width=True)

