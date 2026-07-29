import requests
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import time
from config import API_KEY

symbol = "RKLB"
api_key = API_KEY
UPDATE_INTERVAL_SECONDS = 3600  # Data only changes once/day on the free tier, so check hourly
HEARTBEAT_SECONDS = 15          # How often to print a "still monitoring" message


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


def update():
    try:
        df = get_data()
        if df is None:
            print("API error or rate limit reached. Retrying next cycle...")
            return None

        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc,
                                    gridstyle='--', gridcolor='#dddddd')

        fig, axlist = mpf.plot(
            df,
            type='candle',
            style=style,
            mav=(20, 50),
            volume=True,
            title=f"\n{symbol} - Rocket Lab Stock Price",
            ylabel='Price (USD)',
            ylabel_lower='Volume',
            returnfig=True,
            figsize=(14, 8)
        )

        ax_price = axlist[0]

        current_price = df['Close'].iloc[-1]
        first_price = df['Close'].iloc[0]
        change_pct = ((current_price - first_price) / first_price) * 100
        change_color = "#00994d" if change_pct >= 0 else "#cc0000"
        change_sign = "+" if change_pct >= 0 else ""

        badge_text = f"{symbol}\n${current_price:.2f}  {change_sign}{change_pct:.2f}%"
        ax_price.text(0.01, 0.97, badge_text, transform=ax_price.transAxes, fontsize=12,
                      verticalalignment='top', color=change_color, fontweight='bold',
                      bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                                edgecolor=change_color, linewidth=1.3))

        return fig

    except Exception as e:
        print(f"Error in update(): {e}")
        return None


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

            current_fig = update()

            if current_fig is not None:
                print(f"Chart updated at {time.strftime('%H:%M:%S')}.")

            plt.pause(0.5)

            for i in range(UPDATE_INTERVAL_SECONDS):
                plt.pause(1)
                seconds_left = UPDATE_INTERVAL_SECONDS - (i + 1)
                if seconds_left % HEARTBEAT_SECONDS == 0 and seconds_left != 0:
                    print(f"   ...monitoring. Next update in {seconds_left}s")

        except KeyboardInterrupt:
            print("\nMonitor stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}. Retrying in {UPDATE_INTERVAL_SECONDS}s")
            time.sleep(UPDATE_INTERVAL_SECONDS)
