from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN
from stocks import get_data, calculate_rsi, rsi_status


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


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).connect_timeout(30).read_timeout(30).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()
