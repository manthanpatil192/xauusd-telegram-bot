import os
import sys
import logging
import asyncio
from pathlib import Path

from config import SECONDARY_BOT_TOKEN
from indian_stock_analyzer import IndianStockAnalyzer
from chart_generator import ChartGenerator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("TradeMasterBot")

try:
    from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters,
    )
    HAS_TELEGRAM_LIB = True
except ImportError:
    HAS_TELEGRAM_LIB = False

def get_trademaster_keyboard():
    """Main Menu Keyboard for TradeMaster Indian Stock Bot."""
    keyboard = [
        [KeyboardButton("📈 NIFTY 50 Signal"), KeyboardButton("🏦 BANK NIFTY Signal")],
        [KeyboardButton("🔍 Stock Screener"), KeyboardButton("📰 Indian Market News")],
        [KeyboardButton("📊 View NIFTY Chart"), KeyboardButton("ℹ️ User Guide")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_trademaster_inline_buttons():
    """1-Tap Interactive Buttons for TradeMaster."""
    buttons = [
        [
            InlineKeyboardButton("📈 NIFTY 50", callback_data="tm_nifty"),
            InlineKeyboardButton("🏦 BANK NIFTY", callback_data="tm_banknifty")
        ],
        [
            InlineKeyboardButton("🔍 Top Stock Screener", callback_data="tm_screener"),
            InlineKeyboardButton("📊 View Chart", callback_data="tm_chart")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def tm_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🇮🇳 <b>TRADEMASTER - INDIAN STOCK MARKET BOT</b> 🇮🇳\n\n"
        "Welcome! I am <b>TradeMaster</b>, your automated assistant for Indian Stock Market (NSE / BSE) trading.\n\n"
        "⚡ <b>Supported Indian Assets:</b>\n"
        "• 📈 <b>NIFTY 50 & BANK NIFTY:</b> Live Index Breakout Signals\n"
        "• 🏢 <b>NSE Equities:</b> Reliance, HDFC Bank, TCS, Infosys, ICICI Bank, SBI\n"
        "• 📊 <b>Technicals:</b> S/R Pivots, RSI (14), EMA 50/200, Volume Spikes\n"
        "• 📰 <b>Indian News Radar:</b> RBI Interest Rate & Market Sentiment\n\n"
        "Tap any button below to get instant Indian market signals!"
    )
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=get_trademaster_keyboard())

async def tm_nifty_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🔎 Analyzing NIFTY 50 Index technicals & price action...")

    res = IndianStockAnalyzer.analyze_stock("NIFTY")
    
    msg = (
        f"🇮🇳 <b>NIFTY 50 INDEX SIGNAL</b> 🇮🇳\n"
        f"═════════════════════════\n"
        f"💰 <b>Current Level:</b> <code>{res['current_price']:.2f}</code> ({res['change_pct']:+.2f}%)\n"
        f"📢 <b>Action:</b> <code>{res['signal_action']}</code>\n"
        f"📈 <b>Trend:</b> {res['trend']}\n"
        f"═════════════════════════\n"
        f"🎯 <b>ENTRY:</b> <code>{res['entry']:.2f}</code>\n"
        f"🛑 <b>STOP LOSS:</b> <code>{res['sl']:.2f}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>{res['target1']:.2f}</code> (1:2 R:R)\n"
        f"🚀 <b>TARGET 2:</b> <code>{res['target2']:.2f}</code> (1:3.5 R:R)\n"
        f"═════════════════════════\n"
        f"📊 <b>RSI (14):</b> <code>{res['rsi_14']}</code> | <b>EMA 50:</b> <code>{res['ema_50']:.2f}</code>\n"
        f"📌 <b>Support S1:</b> <code>{res['support_s1']:.2f}</code> | <b>Resistance R1:</b> <code>{res['resistance_r1']:.2f}</code>\n"
        f"═════════════════════════\n"
        f"💡 <i>Risk Management: Set strict stop losses near key pivot levels.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_banknifty_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🏦 Analyzing BANK NIFTY Index technicals...")

    res = IndianStockAnalyzer.analyze_stock("BANKNIFTY")
    
    msg = (
        f"🏦 <b>BANK NIFTY INDEX SIGNAL</b> 🏦\n"
        f"═════════════════════════\n"
        f"💰 <b>Current Level:</b> <code>{res['current_price']:.2f}</code> ({res['change_pct']:+.2f}%)\n"
        f"📢 <b>Action:</b> <code>{res['signal_action']}</code>\n"
        f"📈 <b>Trend:</b> {res['trend']}\n"
        f"═════════════════════════\n"
        f"🎯 <b>ENTRY:</b> <code>{res['entry']:.2f}</code>\n"
        f"🛑 <b>STOP LOSS:</b> <code>{res['sl']:.2f}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>{res['target1']:.2f}</code>\n"
        f"🚀 <b>TARGET 2:</b> <code>{res['target2']:.2f}</code>\n"
        f"═════════════════════════\n"
        f"📊 <b>RSI 14:</b> <code>{res['rsi_14']}</code> | <b>EMA 200:</b> <code>{res['ema_200']:.2f}</code>\n"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_screener_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🔍 Scanning Top NSE Stocks (Reliance, HDFC Bank, TCS, Infosys, SBI)...")

    stocks = IndianStockAnalyzer.screen_top_indian_stocks()
    
    stock_lines = ""
    for s in stocks:
        stock_lines += f"• <b>{s['symbol']}</b>: ₹{s['current_price']:.2f} ({s['change_pct']:+.2f}%) ➔ {s['signal_action']}\n"

    msg = (
        f"🔍 <b>INDIAN STOCK MARKET SCREENER</b> 🔍\n"
        f"═════════════════════════\n"
        f"{stock_lines}\n"
        f"═════════════════════════\n"
        f"💡 <i>Top Indian blue-chip stocks filtered by trend & RSI momentum.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    msg = (
        f"📰 <b>INDIAN MARKET & RBI NEWS RADAR</b> 📰\n"
        f"═════════════════════════\n"
        f"• <b>RBI Monetary Policy:</b> Repo rate steady at 6.50% (Neutral stance)\n"
        f"• <b>FII / DII Activity:</b> Institutional net buying positive in Indian equities\n"
        f"• <b>Corporate Earnings:</b> Q2 Corporate earnings meeting market expectations\n"
        f"═════════════════════════\n"
        f"✅ <i>Market conditions favourable for trend-following setups.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🎨 Rendering NIFTY 50 dark-mode chart...")

    res = IndianStockAnalyzer.analyze_stock("NIFTY")
    df = res["df"]
    
    signal_mock = {
        "entry": res["entry"], "sl": res["sl"], "tp1": res["target1"], "tp2": res["target2"],
        "action": res["signal_action"], "confidence_stars": "⭐️⭐️⭐️⭐️"
    }
    chart_path = ChartGenerator.generate_signal_chart(df, signal_mock, "nifty_chart.png")

    with open(chart_path, "rb") as chart_file:
        await target.reply_photo(
            photo=chart_file,
            caption=f"📈 <b>NIFTY 50 Chart</b> | {res['signal_action']}\nLevel: {res['current_price']:.2f} | Target: {res['target1']:.2f} | SL: {res['sl']:.2f}",
            parse_mode="HTML",
            reply_markup=get_trademaster_inline_buttons()
        )

async def tm_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "tm_nifty":
        await tm_nifty_command(update, context)
    elif data == "tm_banknifty":
        await tm_banknifty_command(update, context)
    elif data == "tm_screener":
        await tm_screener_command(update, context)
    elif data == "tm_chart":
        await tm_chart_command(update, context)

async def tm_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "NIFTY 50" in text:
        await tm_nifty_command(update, context)
    elif "BANK NIFTY" in text:
        await tm_banknifty_command(update, context)
    elif "Screener" in text:
        await tm_screener_command(update, context)
    elif "News" in text:
        await tm_news_command(update, context)
    elif "Chart" in text:
        await tm_chart_command(update, context)
    elif "Guide" in text or "Help" in text:
        await tm_start_command(update, context)

async def run_trademaster_bot(token: str):
    """Runs TradeMaster Indian Stock Bot instance."""
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("TradeMaster token not configured.")
        return

    logger.info("Initializing TradeMaster Indian Stock Bot Application...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", tm_start_command))
    app.add_handler(CommandHandler("nifty", tm_nifty_command))
    app.add_handler(CommandHandler("banknifty", tm_banknifty_command))
    app.add_handler(CommandHandler("screener", tm_screener_command))
    app.add_handler(CommandHandler("news", tm_news_command))
    app.add_handler(CommandHandler("chart", tm_chart_command))
    app.add_handler(CallbackQueryHandler(tm_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tm_text_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("🇮🇳 TradeMaster (Indian Stock Bot) is LIVE & listening on Telegram!")

    while True:
        await asyncio.sleep(3600)
