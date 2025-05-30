import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
import requests
import pandas as pd
import ta

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def get_crypto_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    res = requests.get(url).json()
    price = res.get(symbol, {}).get("usd")
    return price

def get_xauusd_data():
    data = yf.download("XAUUSD=X", period="7d", interval="1h")
    return data

def analyze_xauusd():
    df = get_xauusd_data()
    df.dropna(inplace=True)
    df['ema50'] = ta.trend.ema_indicator(df['Close'], window=50).ema_indicator()
    df['ema200'] = ta.trend.ema_indicator(df['Close'], window=200).ema_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()

    latest = df.iloc[-1]
    trend = "Bullish 📈" if latest['ema50'] > latest['ema200'] else "Bearish 📉"
    rsi = latest['rsi']
    suggestion = "BUY on dip di sekitar {:.2f}".format(latest['Close'] * 0.99) if trend == "Bullish 📈" else "SELL on rally di sekitar {:.2f}".format(latest['Close'] * 1.01)
    sl = latest['Close'] * (0.99 if trend == "Bullish 📈" else 1.01)
    tp = latest['Close'] * (1.01 if trend == "Bullish 📈" else 0.99)

    return (
        f"Analisa XAUUSD (TF: 1H)\n"
        f"Trend: {trend}\n"
        f"RSI: {rsi:.2f}\n"
        f"Saran Entry: {suggestion}\n"
        f"SL: {sl:.2f} | TP: {tp:.2f}"
    )

async def harga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        symbol = context.args[0].lower()
        if symbol == "xauusd":
            data = yf.download("XAUUSD=X", period="1d", interval="1m")
            price = data['Close'].iloc[-1]
            await update.message.reply_text(f"XAU/USD Harga Saat Ini: ${price:.2f}")
        else:
            price = get_crypto_price(symbol)
            if price:
                await update.message.reply_text(f"{symbol.upper()} Harga Saat Ini: ${price:.2f}")
            else:
                await update.message.reply_text("Symbol tidak ditemukan.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def analisa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        analysis = analyze_xauusd()
        await update.message.reply_text(analysis)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim /harga btc atau /harga xauusd untuk cek harga.\nGunakan /analisa untuk saran entry XAUUSD.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("harga", harga))
    app.add_handler(CommandHandler("analisa", analisa))
    app.run_polling()

if __name__ == '__main__':
    main()
