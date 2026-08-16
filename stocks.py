import requests
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import time
from config import API_KEY

symbol = "RKLB"
api_key = API_KEY
UPDATE_INTERVAL_SECONDS = 3600
HEARTBEAT_SECONDS = 15


def get_data():
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if 'Error Message' in data or 'Time Series (Daily)' not in data:
        return None

    time_series = data['Time Series (Daily)']

    records = []
    for day in time_series:
        entry = time_series[day]
        records.append({
            'Date': day,
            'Open': float(entry['1. open']),
            'High': float(entry['2. high']),
            'Low': float(entry['3. low']),
            'Close': float(entry['4. close']),
            'Volume': float(entry['5. volume'])
        })

    df = pd.DataFrame(records)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    return df


def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_vwap(df):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    tp_volume = typical_price * df['Volume']
    cumulative_tp_volume = tp_volume.cumsum()
    cumulative_volume = df['Volume'].cumsum()
    return cumulative_tp_volume / cumulative_volume


def calculate_bollinger_bands(df, period=20):
    middle = df['Close'].rolling(period).mean()
    std = df['Close'].rolling(period).std()
    upper = middle + (2 * std)
    lower = middle - (2 * std)
    return middle, upper, lower


def get_hod_lod(df):
    hod = df['High'].iloc[-1]
    lod = df['Low'].iloc[-1]
    return hod, lod


def rsi_status(rsi_value):
    if rsi_value < 30:
        return "OVERSOLD"
    elif rsi_value > 70:
        return "OVERBOUGHT"
    else:
        return "NEUTRAL"


def update():
    try:
        df = get_data()
        if df is None:
            print("API error or rate limit reached. Retrying next cycle...")
            return None, None

        df['RSI'] = calculate_rsi(df)
        df['VWAP'] = calculate_vwap(df)
        bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(df)
        df['BB_upper'] = bb_upper
        df['BB_lower'] = bb_lower
        hod, lod = get_hod_lod(df)

        current_rsi = df['RSI'].iloc[-1]
        rsi_label = rsi_status(current_rsi)

        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc,
                                    gridstyle='--', gridcolor='#dddddd')

        rsi_plot = mpf.make_addplot(df['RSI'], panel=2, color='#7e57c2', ylabel='RSI')
        vwap_plot = mpf.make_addplot(df['VWAP'], panel=0, color='#9c27b0', width=1.2, label='VWAP')
        bb_upper_plot = mpf.make_addplot(df['BB_upper'], panel=0, color='#90a4ae', linestyle='--', width=0.8, label='Bollinger Bands')
        bb_lower_plot = mpf.make_addplot(df['BB_lower'], panel=0, color='#90a4ae', linestyle='--', width=0.8)

        fig, axlist = mpf.plot(
            df,
            type='candle',
            style=style,
            mav=(20, 50),
            volume=True,
            addplot=[rsi_plot, vwap_plot, bb_upper_plot, bb_lower_plot],
            panel_ratios=(6, 2, 2),
            title=f"\n{symbol} - Rocket Lab Stock Price",
            ylabel='Price (USD)',
            ylabel_lower='Volume',
            returnfig=True,
            figsize=(14, 9)
        )

        ax_price = axlist[0]
        ax_volume = axlist[2]
        ax_rsi = axlist[4]

        ax_price.axhline(hod, color='#2e7d32', linestyle=':', linewidth=1, alpha=0.7)
        ax_price.axhline(lod, color='#c62828', linestyle=':', linewidth=1, alpha=0.7)

        legend_elements = [
            Line2D([0], [0], color='#1f77b4', lw=1.2, label='SMA 20'),
            Line2D([0], [0], color='#ff7f0e', lw=1.2, label='SMA 50'),
            Line2D([0], [0], color='#9c27b0', lw=1.2, label='VWAP'),
            Line2D([0], [0], color='#90a4ae', lw=0.8, linestyle='--', label='Bollinger Bands'),
            Line2D([0], [0], color='#2e7d32', lw=1, linestyle=':', label='HOD'),
            Line2D([0], [0], color='#c62828', lw=1, linestyle=':', label='LOD'),
        ]
        ax_price.legend(handles=legend_elements, loc='upper right', fontsize=8, framealpha=0.9)

        ax_price.yaxis.set_major_locator(MaxNLocator(nbins=7))
        ax_price.yaxis.set_major_formatter(lambda x, pos: f"${x:.0f}")
        ax_price.grid(True, linestyle='--', alpha=0.4)

        ax_volume.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax_volume.grid(True, linestyle='--', alpha=0.4)

        ax_rsi.set_yticks(range(0, 101, 20))
        ax_rsi.grid(True, linestyle='--', alpha=0.4)

        for ax in [ax_price, ax_volume]:
            pos = ax.get_position()
            divider = Line2D([pos.x0, pos.x1], [pos.y0, pos.y0],
                              transform=fig.transFigure, color='black', linewidth=1.5)
            fig.add_artist(divider)

        ax_rsi.axhline(70, color='#cc0000', linestyle='--', linewidth=0.8, alpha=0.6)
        ax_rsi.axhline(30, color='#00994d', linestyle='--', linewidth=0.8, alpha=0.6)
        ax_rsi.set_ylim(0, 100)

        current_price = df['Close'].iloc[-1]
        previous_close = df['Close'].iloc[-2]
        daily_change_pct = ((current_price - previous_close) / previous_close) * 100
        change_color = "#00994d" if daily_change_pct >= 0 else "#cc0000"
        change_sign = "+" if daily_change_pct >= 0 else ""

        badge_text = (f"{symbol}\n"
                      f"${current_price:.2f}  {change_sign}{daily_change_pct:.2f}% (1d)\n"
                      f"RSI(14): {current_rsi:.1f} - {rsi_label}")
        ax_price.text(0.01, 0.97, badge_text, transform=ax_price.transAxes, fontsize=11,
                      verticalalignment='top', color=change_color, fontweight='bold',
                      bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                                edgecolor=change_color, linewidth=1.3))

        summary = {
            'price': current_price,
            'change_pct': daily_change_pct,
            'volume': df['Volume'].iloc[-1],
            'last_date': df.index[-1].strftime('%Y-%m-%d'),
            'rsi': current_rsi,
            'rsi_label': rsi_label
        }

        return fig, summary

    except Exception as e:
        print(f"Error in update(): {e}")
        return None, None


if __name__ == "__main__":
    plt.ion()

    print("RKLB Stock Monitor started.")
    print(f"Data refresh: every {UPDATE_INTERVAL_SECONDS}s | Heartbeat: every {HEARTBEAT_SECONDS}s")
    print("Close the window to stop the program.\n")

    current_fig = None

    while True:
        try:
            if current_fig is not None:
                plt.close(current_fig)

            current_fig, summary = update()

            if current_fig is not None:
                try:
                    mng = current_fig.canvas.manager
                    mng.window.state('zoomed')
                except Exception:
                    pass

                sign = "+" if summary['change_pct'] >= 0 else ""
                print(f"Chart updated at {time.strftime('%H:%M:%S')} "
                      f"| Last close ({summary['last_date']}): ${summary['price']:.2f} "
                      f"({sign}{summary['change_pct']:.2f}%) "
                      f"| Volume: {summary['volume']/1e6:.1f}M "
                      f"| RSI: {summary['rsi']:.1f} ({summary['rsi_label']})")

            plt.pause(0.5)

            for i in range(UPDATE_INTERVAL_SECONDS):
                plt.pause(1)
                seconds_left = UPDATE_INTERVAL_SECONDS - (i + 1)
                if seconds_left % HEARTBEAT_SECONDS == 0 and seconds_left != 0:
                    mins, secs = divmod(seconds_left, 60)
                    print(f"   [{time.strftime('%H:%M:%S')}] Monitoring... next check in {mins}m {secs}s")

        except KeyboardInterrupt:
            print("\nMonitor stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in {UPDATE_INTERVAL_SECONDS}s")
            time.sleep(UPDATE_INTERVAL_SECONDS)
