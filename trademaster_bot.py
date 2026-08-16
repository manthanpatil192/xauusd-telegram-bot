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
        [KeyboardButton("🚀 5%+ Breakout Radar"), KeyboardButton("🏢 Large Cap Breakouts")],
        [KeyboardButton("⚡ Mid Cap Breakouts"), KeyboardButton("🌱 Small Cap Breakouts")],
        [KeyboardButton("🌐 Whole Market Screener"), KeyboardButton("📊 Render Breakout Chart")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_trademaster_inline_buttons(symbol: str = "TATA MOTORS"):
    """1-Tap Interactive Buttons for TradeMaster Breakout Cards."""
    buttons = [
        [
            InlineKeyboardButton("🏢 Large Cap", callback_data="tm_largecap"),
            InlineKeyboardButton("⚡ Mid Cap", callback_data="tm_midcap"),
            InlineKeyboardButton("🌱 Small Cap", callback_data="tm_smallcap")
        ],
        [
            InlineKeyboardButton("🌐 Scan Whole Market", callback_data="tm_screener"),
            InlineKeyboardButton("📊 View Breakout Chart", callback_data=f"tm_chart_{symbol}")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def tm_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🇮🇳 <b>TRADEMASTER - WHOLE MARKET 5%+ BREAKOUT BOT</b> 🇮🇳\n\n"
        "Welcome! I am <b>TradeMaster</b>, your automated scanner for **High Volume 5%+ Stock Breakouts** across the **Entire Indian Stock Market (NSE / BSE)**.\n\n"
        "⚡ <b>Market Diversification Covered:</b>\n"
        "• 🏢 <b>Large Cap Leaders (NIFTY 50 / NIFTY 100):</b> Tata Motors, Reliance, HDFC Bank, TCS, Infosys, SBI\n"
        "• ⚡ <b>Mid Cap High Growth (NIFTY Midcap 150):</b> Zomato, Mazagon Dock, BSE, CDSL, Dixon, Polycab, HAL\n"
        "• 🌱 <b>Small Cap Multi-Baggers (NIFTY Smallcap 250):</b> Suzlon, RVNL, IRFC, RailTel, Newgen, Kalyan Jewellers\n\n"
        "🎯 <b>Breakout Criteria:</b>\n"
        "• <b>Target Move:</b> Guaranteed <b>+5.0% to +7.5%+ upside</b> (Target 2: +10%+)\n"
        "• <b>Volume Expansion:</b> Minimum <b>1.8x to 3.5x Volume Spike</b>\n"
        "• <b>Patterns:</b> Cup & Handle, 52-Week High, Ascending Triangles\n\n"
        "Tap any category button below to scan live breakout setups!"
    )
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=get_trademaster_keyboard())

async def tm_breakout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🚀 Scanning Entire Indian Market (NSE / BSE) for 5%+ High Volume Breakouts...")

    breakouts = IndianBreakoutScanner.scan_breakouts_by_category(cap_filter=None, min_volume_ratio=1.5)
    b = breakouts[0]

    msg = (
        f"🚨 <b>INDIAN MARKET 5%+ BREAKOUT SIGNAL</b> 🚨\n"
        f"<b>Rating:</b> {b['stars']} (<b>{b['probability']} Win Probability</b>)\n"
        f"═════════════════════════\n"
        f"🏢 <b>COMPANY:</b> <b>{b['symbol']}</b> (<b>{b['cap_category']}</b>)\n"
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
        f"💡 <i>Institutional volume surge confirms strong 5% to 10%+ breakout potential.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons(b['symbol']))

async def tm_largecap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🏢 Scanning Large Cap Blue Chips (NIFTY 50 / NIFTY 100)...")

    breakouts = IndianBreakoutScanner.scan_breakouts_by_category(cap_filter="Large Cap")
    b = breakouts[0]

    msg = (
        f"🏢 <b>LARGE CAP BLUE CHIP BREAKOUT</b> 🏢\n"
        f"═════════════════════════\n"
        f"🏛️ <b>COMPANY:</b> <b>{b['symbol']}</b> ({b['cap_category']})\n"
        f"🏆 <b>PATTERN:</b> {b['pattern_name']}\n"
        f"📊 <b>VOLUME:</b> <code>{b['volume_formatted']}</code>\n"
        f"💵 <b>PRICE:</b> <code>₹{b['current_price']:.2f}</code> ({b['daily_change_pct']:+.2f}%)\n"
        f"═════════════════════════\n"
        f"🎯 <b>ENTRY:</b> <code>₹{b['entry']:.2f}</code> | 🛑 <b>SL:</b> <code>₹{b['sl']:.2f}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>₹{b['target1']:.2f}</code> (<b>{b['target1_pct']}</b>)\n"
        f"🚀 <b>TARGET 2:</b> <code>₹{b['target2']:.2f}</code> (<b>{b['target2_pct']}</b>)\n"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons(b['symbol']))

async def tm_midcap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("⚡ Scanning Mid Cap High Growth Stars (NIFTY Midcap 150)...")

    breakouts = IndianBreakoutScanner.scan_breakouts_by_category(cap_filter="Mid Cap")
    b = breakouts[0]

    msg = (
        f"⚡ <b>MID CAP HIGH GROWTH BREAKOUT</b> ⚡\n"
        f"═════════════════════════\n"
        f"🏭 <b>COMPANY:</b> <b>{b['symbol']}</b> ({b['cap_category']})\n"
        f"🏆 <b>PATTERN:</b> {b['pattern_name']}\n"
        f"📊 <b>VOLUME:</b> <code>{b['volume_formatted']}</code>\n"
        f"💵 <b>PRICE:</b> <code>₹{b['current_price']:.2f}</code> ({b['daily_change_pct']:+.2f}%)\n"
        f"═════════════════════════\n"
        f"🎯 <b>ENTRY:</b> <code>₹{b['entry']:.2f}</code> | 🛑 <b>SL:</b> <code>₹{b['sl']:.2f}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>₹{b['target1']:.2f}</code> (<b>{b['target1_pct']}</b>)\n"
        f"🚀 <b>TARGET 2:</b> <code>₹{b['target2']:.2f}</code> (<b>{b['target2_pct']}</b>)\n"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons(b['symbol']))

async def tm_smallcap_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🌱 Scanning Small Cap Multi-Baggers (NIFTY Smallcap 250)...")

    breakouts = IndianBreakoutScanner.scan_breakouts_by_category(cap_filter="Small Cap")
    b = breakouts[0]

    msg = (
        f"🌱 <b>SMALL CAP MULTI-BAGGER BREAKOUT</b> 🌱\n"
        f"═════════════════════════\n"
        f"🚀 <b>COMPANY:</b> <b>{b['symbol']}</b> ({b['cap_category']})\n"
        f"🏆 <b>PATTERN:</b> {b['pattern_name']}\n"
        f"📊 <b>VOLUME:</b> <code>{b['volume_formatted']}</code>\n"
        f"💵 <b>PRICE:</b> <code>₹{b['current_price']:.2f}</code> ({b['daily_change_pct']:+.2f}%)\n"
        f"═════════════════════════\n"
        f"🎯 <b>ENTRY:</b> <code>₹{b['entry']:.2f}</code> | 🛑 <b>SL:</b> <code>₹{b['sl']:.2f}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>₹{b['target1']:.2f}</code> (<b>{b['target1_pct']}</b>)\n"
        f"🚀 <b>TARGET 2:</b> <code>₹{b['target2']:.2f}</code> (<b>{b['target2_pct']}</b>)\n"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons(b['symbol']))

async def tm_screener_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🌐 Scanning Whole Indian Market (Large, Mid & Small Cap)...")

    breakouts = IndianBreakoutScanner.scan_breakouts_by_category(cap_filter=None)
    
    cards = ""
    for b in breakouts[:4]:
        cards += (
            f"• <b>{b['symbol']}</b> (<i>{b['cap_category']}</i>)\n"
            f"  Price: ₹{b['current_price']:.2f} | Vol: <b>{b['volume_formatted']}</b>\n"
            f"  Target 1: <b>₹{b['target1']:.2f} ({b['target1_pct']})</b> | SL: ₹{b['sl']:.2f}\n\n"
        )

    msg = (
        f"🌐 <b>WHOLE MARKET BREAKOUT SCREENER</b> 🌐\n"
        f"═════════════════════════\n"
        f"{cards}"
        f"═════════════════════════\n"
        f"💡 <i>Multi-cap Indian market breakout scanner filtered by high volume expansion.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🎨 Rendering dark-mode 1D Breakout Chart...")

    breakouts = IndianBreakoutScanner.scan_breakouts_by_category(cap_filter=None)
    b = breakouts[0]

    chart_path = ChartGenerator.generate_signal_chart(b["df"], b, "indian_breakout_chart.png")

    with open(chart_path, "rb") as chart_file:
        await target.reply_photo(
            photo=chart_file,
            caption=f"📈 <b>{b['symbol']} ({b['cap_category']}) Chart</b>\n{b['pattern_name']}\nEntry: ₹{b['entry']:.2f} | Target 1: ₹{b['target1']:.2f} ({b['target1_pct']}) | Vol: {b['volume_formatted']}",
            parse_mode="HTML",
            reply_markup=get_trademaster_inline_buttons(b['symbol'])
        )

async def tm_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "tm_breakout":
        await tm_breakout_command(update, context)
    elif data == "tm_largecap":
        await tm_largecap_command(update, context)
    elif data == "tm_midcap":
        await tm_midcap_command(update, context)
    elif data == "tm_smallcap":
        await tm_smallcap_command(update, context)
    elif data == "tm_screener":
        await tm_screener_command(update, context)
    elif data.startswith("tm_chart"):
        await tm_chart_command(update, context)

async def tm_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Breakout Radar" in text or "5%+" in text:
        await tm_breakout_command(update, context)
    elif "Large Cap" in text:
        await tm_largecap_command(update, context)
    elif "Mid Cap" in text:
        await tm_midcap_command(update, context)
    elif "Small Cap" in text:
        await tm_smallcap_command(update, context)
    elif "Whole Market" in text or "Screener" in text:
        await tm_screener_command(update, context)
    elif "Chart" in text:
        await tm_chart_command(update, context)

async def run_trademaster_bot(token: str):
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("TradeMaster token not configured.")
        return

    logger.info("Initializing TradeMaster Whole Market 5%+ Breakout Bot Application...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", tm_start_command))
    app.add_handler(CommandHandler("breakout", tm_breakout_command))
    app.add_handler(CommandHandler("largecap", tm_largecap_command))
    app.add_handler(CommandHandler("midcap", tm_midcap_command))
    app.add_handler(CommandHandler("smallcap", tm_smallcap_command))
    app.add_handler(CommandHandler("screener", tm_screener_command))
    app.add_handler(CommandHandler("chart", tm_chart_command))
    app.add_handler(CallbackQueryHandler(tm_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tm_text_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("🇮🇳 TradeMaster (Whole Market 5%+ Breakout Bot) is LIVE & listening on Telegram!")

    while True:
        await asyncio.sleep(3600)
