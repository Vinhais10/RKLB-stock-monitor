import matplotlib
matplotlib.use('Agg')

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN
from stocks import get_data, calculate_rsi, calculate_vwap, calculate_bollinger_bands, rsi_status
import mplfinance as mpf
import matplotlib.pyplot as plt


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! RKLB Monitor Bot is online.")


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

    sign = "+" if change_pct >= 0 else ""
    message = (f"RKLB: ${current_price:.2f} ({sign}{change_pct:.2f}%)\n"
               f"RSI(14): {current_rsi:.1f} ({label})")
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

        mc = mpf.make_marketcolors(up='#26a69a', down='#ef5350', inherit=True)
        style = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc, gridstyle='--', gridcolor='#dddddd')

        mpf.plot(df, type='candle', style=style, mav=(20, 50), volume=True,
                 title="RKLB - Rocket Lab Stock Price", savefig='chart.png')
        plt.close('all')

        await update.message.reply_photo(photo=open('chart.png', 'rb'))

    except Exception as e:
        await update.message.reply_text(f"Error generating chart: {e}")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).connect_timeout(30).read_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("chart", chart))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()
