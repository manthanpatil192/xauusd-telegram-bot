import os
import sys
import logging
import asyncio
from pathlib import Path

from config import SECONDARY_BOT_TOKEN
from indian_breakout_scanner import IndianBreakoutScanner
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
    """Main Menu Keyboard for TradeMaster Indian Stock Breakout Bot."""
    keyboard = [
        [KeyboardButton("🚀 5%+ Breakout Radar"), KeyboardButton("📈 High Volume Surge")],
        [KeyboardButton("🏢 Small & Mid Cap Radar"), KeyboardButton("📊 Render Breakout Chart")],
        [KeyboardButton("ℹ️ Breakout Strategy Guide")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_trademaster_inline_buttons(symbol: str = "SUZLON"):
    """1-Tap Interactive Buttons for TradeMaster Breakout Cards."""
    buttons = [
        [
            InlineKeyboardButton("🚀 Scan 5%+ Breakouts", callback_data="tm_breakout"),
            InlineKeyboardButton("📈 High Volume Surge", callback_data="tm_volume")
        ],
        [
            InlineKeyboardButton("🏢 Small/Mid Cap Radar", callback_data="tm_smallcap"),
            InlineKeyboardButton("📊 View Breakout Chart", callback_data=f"tm_chart_{symbol}")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def tm_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🇮🇳 <b>TRADEMASTER - HIGH VOLUME BREAKOUT BOT</b> 🇮🇳\n\n"
        "Welcome! I am <b>TradeMaster</b>, your automated scanner for **High Volume 5%+ Stock Breakouts** across the Indian Stock Market (NSE / BSE).\n\n"
        "⚡ <b>Breakout Engine Capabilities (Daily 1D Timeframe):</b>\n"
        "• 🚀 <b>Target Move:</b> Minimum <b>+5% to +7%+ single-day/short-term upside</b>\n"
        "• 🏆 <b>Patterns Detected:</b> Cup & Handle, 52-Week High, Ascending Triangle Breakouts\n"
        "• 📊 <b>Volume Multiplier:</b> Flags stocks with <b>2.0x+ Volume Expansion</b>\n"
        "• 🏢 <b>Market Coverage:</b> Small Cap, Mid Cap & Large Cap NSE Equities\n"
        "• 🎯 <b>Levels Provided:</b> Confirmed Entry Zone, Stop Loss, Target 1 (+5%), Target 2 (+10%+)\n\n"
        "Tap <b>🚀 5%+ Breakout Radar</b> below to scan live breakout setups!"
    )
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=get_trademaster_keyboard())

async def tm_breakout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🚀 Scanning Daily 1D charts for High Volume 5%+ Stock Breakouts...")

    breakouts = IndianBreakoutScanner.scan_all_breakouts(min_volume_ratio=1.5)
    
    if not breakouts:
        await target.reply_text("🔎 No valid 5%+ high-volume breakouts detected right now. Re-scanning...")
        return

    # Take top high-volume breakout
    b = breakouts[0]
    
    msg = (
        f"🚨 <b>INDIAN MARKET 5%+ BREAKOUT SIGNAL</b> 🚨\n"
        f"<b>Rating:</b> {b['stars']} (<b>{b['probability']} Probability</b>)\n"
        f"═════════════════════════\n"
        f"🏢 <b>COMPANY:</b> <b>{b['symbol']}</b> ({b['cap_category']})\n"
        f" sector: {b['sector']} | Ticker: <code>{b['ticker']}</code>\n"
        f"🏆 <b>PATTERN:</b> {b['pattern_name']}\n"
        f"📊 <b>VOLUME SURGE:</b> <code>{b['volume_formatted']}</code> (High Expansion 🔥)\n"
        f"💵 <b>CURRENT PRICE:</b> <code>₹{b['current_price']:.2f}</code> ({b['daily_change_pct']:+.2f}%)\n"
        f"═════════════════════════\n"
        f"🎯 <b>CONFIRMED ENTRY:</b> <code>₹{b['entry']:.2f}</code>\n"
        f"🛑 <b>STOP LOSS:</b> <code>₹{b['sl']:.2f}</code> (-2.8% Risk)\n"
        f"✅ <b>TARGET 1 (Min Upside):</b> <code>₹{b['target1']:.2f}</code> (<b>{b['target1_pct']}</b>)\n"
        f"🚀 <b>TARGET 2 (Extended):</b> <code>₹{b['target2']:.2f}</code> (<b>{b['target2_pct']}</b>)\n"
        f"═════════════════════════\n"
        f"💡 <i>High volume confirms strong institutional buying interest. Target minimum +5% upside move.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons(b['symbol']))

async def tm_volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("📈 Scanning Indian Stocks experiencing 2.0x+ Volume Expansion today...")

    breakouts = IndianBreakoutScanner.scan_all_breakouts(min_volume_ratio=1.8)
    
    cards = ""
    for b in breakouts[:3]:
        cards += (
            f"• <b>{b['symbol']}</b> ({b['cap_category']})\n"
            f"  Price: ₹{b['current_price']:.2f} ({b['daily_change_pct']:+.2f}%)\n"
            f"  Volume: <b>{b['volume_formatted']}</b> | Target: <b>₹{b['target1']:.2f} ({b['target1_pct']})</b>\n\n"
        )

    msg = (
        f"📈 <b>HIGH VOLUME SURGE RADAR (2.0x+ VOLUME)</b> 📈\n"
        f"═════════════════════════\n"
        f"{cards}"
        f"═════════════════════════\n"
        f"💡 <i>Volume expansion precedes massive 5% to 10%+ multi-day price rallies.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_smallcap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🏢 Scanning Small Cap & Mid Cap Multi-Bagger Breakout Setups...")

    breakouts = IndianBreakoutScanner.scan_all_breakouts(min_volume_ratio=1.2)
    small_mid = [b for b in breakouts if b["cap_category"] in ["Small Cap", "Mid Cap"]]

    cards = ""
    for b in small_mid[:3]:
        cards += (
            f"🚀 <b>{b['symbol']}</b> ({b['cap_category']} - {b['sector']})\n"
            f"  Entry: <b>₹{b['entry']:.2f}</b> | SL: <b>₹{b['sl']:.2f}</b>\n"
            f"  Target 1: <b>₹{b['target1']:.2f} ({b['target1_pct']})</b> | Target 2: <b>₹{b['target2']:.2f} ({b['target2_pct']})</b>\n"
            f"  Pattern: <i>{b['pattern_name']}</i>\n\n"
        )

    msg = (
        f"🏢 <b>SMALL & MID CAP BREAKOUT RADAR</b> 🏢\n"
        f"═════════════════════════\n"
        f"{cards}"
        f"═════════════════════════\n"
        f"💡 <i>Small and Mid Cap breakout setups carry the highest single-day 5% to 12%+ rally potential.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🎨 Rendering dark-mode Breakout Chart with Resistance Line & Volume Subplot...")

    breakouts = IndianBreakoutScanner.scan_all_breakouts(min_volume_ratio=1.2)
    b = breakouts[0]

    chart_path = ChartGenerator.generate_signal_chart(b["df"], b, "indian_breakout_chart.png")

    with open(chart_path, "rb") as chart_file:
        await target.reply_photo(
            photo=chart_file,
            caption=f"📈 <b>{b['symbol']} 1D Breakout Chart</b>\n{b['pattern_name']}\nEntry: ₹{b['entry']:.2f} | Target 1: ₹{b['target1']:.2f} ({b['target1_pct']}) | Volume: {b['volume_formatted']}",
            parse_mode="HTML",
            reply_markup=get_trademaster_inline_buttons(b['symbol'])
        )

async def tm_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "tm_breakout":
        await tm_breakout_command(update, context)
    elif data == "tm_volume":
        await tm_volume_command(update, context)
    elif data == "tm_smallcap":
        await tm_smallcap_command(update, context)
    elif data.startswith("tm_chart"):
        await tm_chart_command(update, context)

async def tm_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Breakout" in text:
        await tm_breakout_command(update, context)
    elif "Volume" in text:
        await tm_volume_command(update, context)
    elif "Small" in text or "Mid" in text:
        await tm_smallcap_command(update, context)
    elif "Chart" in text:
        await tm_chart_command(update, context)
    elif "Guide" in text or "Help" in text:
        await tm_start_command(update, context)

async def run_trademaster_bot(token: str):
    """Runs TradeMaster High-Volume 5%+ Indian Stock Breakout Bot."""
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("TradeMaster token not configured.")
        return

    logger.info("Initializing TradeMaster 5%+ Indian Breakout Bot Application...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", tm_start_command))
    app.add_handler(CommandHandler("breakout", tm_breakout_command))
    app.add_handler(CommandHandler("volume", tm_volume_command))
    app.add_handler(CommandHandler("smallcap", tm_smallcap_command))
    app.add_handler(CommandHandler("chart", tm_chart_command))
    app.add_handler(CallbackQueryHandler(tm_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tm_text_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("🇮🇳 TradeMaster (5%+ High Volume Breakout Bot) is LIVE & listening on Telegram!")

    while True:
        await asyncio.sleep(3600)
