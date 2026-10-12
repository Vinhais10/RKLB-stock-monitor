import matplotlib
matplotlib.use('Agg')

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import TELEGRAM_TOKEN, CHAT_ID
from stocks import get_data, calculate_rsi, calculate_vwap, calculate_bollinger_bands, rsi_status
import mplfinance as mpf
import matplotlib.pyplot as plt

ALERT_INTERVAL_SECONDS = 3600
PRICE_MOVE_THRESHOLD_PCT = 5.0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! RKLB Monitor Bot is online.\n\n"
        "Use /help to see available commands."
    )
    print(f"Your chat ID is: {update.message.chat_id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "RKLB Monitor Bot — Commands\n\n"
        "/price — current price, daily change, RSI\n"
        "/chart — full technical chart (candles, SMA, VWAP, Bollinger, volume, RSI)\n"
        "/help — show this message\n\n"
        f"Automatic alerts: RSI overbought/oversold, and price moves of "
        f"{PRICE_MOVE_THRESHOLD_PCT:.0f}%+ in a day — checked every "
        f"{ALERT_INTERVAL_SECONDS // 60} minutes."
    )
    await update.message.reply_text(message)


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = get_data()
    if df is None:
        await update.message.reply_text("Could not fetch data right now. Try again later.")
        return

    df['RSI'] = calculate_rsi(df)
    current_price = df['Close'].iloc[-1]
    previous_close = df['Close'].iloc[-2]
    change_pct = ((current_price - previous_close) / previous_close) * 100
    current_rsi = df['RSI'].iloc[-1]
    label = rsi_status(current_rsi)
    last_date = df.index[-1].strftime('%Y-%m-%d')

    sign = "+" if change_pct >= 0 else ""
    message = (f"RKLB: ${current_price:.2f} ({sign}{change_pct:.2f}%)\n"
               f"RSI(14): {current_rsi:.1f} ({label})\n"
               f"Data as of: {last_date}")
    await update.message.reply_text(message)


async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Generating chart, please wait...")

        df = get_data()
        if df is None:
            await update.message.reply_text("Could not fetch data right now. Try again later.")
            return

        df['RSI'] = calculate_rsi(df)
        df['VWAP'] = calculate_vwap(df)
        bb_middle, bb_upper, bb_lower = calculate_bollinger_bands(df)
        df['BB_upper'] = bb_upper
        df['BB_lower'] = bb_lower
        last_date = df.index[-1].strftime('%Y-%m-%d')

        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc, gridstyle='--', gridcolor='#dddddd')

        mpf.plot(df, type='candle', style=style, mav=(20, 50), volume=True,
                 title=f"RKLB - Rocket Lab Stock Price (as of {last_date})",
                 datetime_format='%b %d', savefig='chart.png')
        plt.close('all')

        await update.message.reply_photo(photo=open('chart.png', 'rb'))

    except Exception as e:
        await update.message.reply_text(f"Error generating chart: {e}")


async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    df = get_data()
    if df is None:
        print("Alert check: could not fetch data.")
        return

    df['RSI'] = calculate_rsi(df)
    current_rsi = df['RSI'].iloc[-1]
    label = rsi_status(current_rsi)

    current_price = df['Close'].iloc[-1]
    previous_close = df['Close'].iloc[-2]
    change_pct = ((current_price - previous_close) / previous_close) * 100

    alerts = []

    if label in ("OVERSOLD", "OVERBOUGHT"):
        alerts.append(f"RSI ALERT: RKLB is {label}\nRSI(14): {current_rsi:.1f}")

    if abs(change_pct) >= PRICE_MOVE_THRESHOLD_PCT:
        direction = "UP" if change_pct >= 0 else "DOWN"
        alerts.append(f"PRICE MOVE ALERT: RKLB is {direction} {abs(change_pct):.2f}% today")

    if alerts:
        for alert_text in alerts:
            full_message = f"{alert_text}\nPrice: ${current_price:.2f}"
            await context.bot.send_message(chat_id=CHAT_ID, text=full_message)
            print(f"Alert sent: {alert_text.splitlines()[0]}")
    else:
        print(f"No alert needed. RSI: {current_rsi:.1f} ({label}), change: {change_pct:.2f}%")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Unknown command. Use /help to see available commands."
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Unhandled error: {context.error}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).connect_timeout(30).read_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("chart", chart))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(check_alerts, interval=ALERT_INTERVAL_SECONDS, first=10)

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()
