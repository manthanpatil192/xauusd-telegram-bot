import os
import sys
import logging
import asyncio
from pathlib import Path

from config import SECONDARY_BOT_TOKEN
from indian_breakout_scanner import IndianBreakoutScanner
from nifty_options_analyzer import NiftyOptionsAnalyzer
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
    """Main Menu Keyboard for TradeMaster Indian Options & Breakouts Bot."""
    keyboard = [
        [KeyboardButton("🎯 NIFTY Call / Put Signal"), KeyboardButton("🏦 BANK NIFTY Call / Put")],
        [KeyboardButton("📊 FII / DII Flow Radar"), KeyboardButton("🚀 5%+ Breakout Radar")],
        [KeyboardButton("🏢 Large Cap Breakouts"), KeyboardButton("⚡ Mid Cap Breakouts")],
        [KeyboardButton("🌱 Small Cap Breakouts"), KeyboardButton("📊 Render Breakout Chart")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_trademaster_inline_buttons(symbol: str = "NIFTY"):
    """1-Tap Interactive Buttons for TradeMaster Options & Breakouts."""
    buttons = [
        [
            InlineKeyboardButton("🎯 NIFTY Call/Put", callback_data="tm_nifty_opt"),
            InlineKeyboardButton("🏦 BANKNIFTY Call/Put", callback_data="tm_banknifty_opt")
        ],
        [
            InlineKeyboardButton("📊 FII / DII Flow", callback_data="tm_fiidii"),
            InlineKeyboardButton("🚀 5%+ Breakouts", callback_data="tm_breakout")
        ],
        [
            InlineKeyboardButton("🏢 Large Cap", callback_data="tm_largecap"),
            InlineKeyboardButton("⚡ Mid Cap", callback_data="tm_midcap"),
            InlineKeyboardButton("🌱 Small Cap", callback_data="tm_smallcap")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def tm_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🇮🇳 <b>TRADEMASTER - OPTIONS & BREAKOUT ENGINE</b> 🇮🇳\n\n"
        "Welcome! I am <b>TradeMaster</b>, your automated assistant for **NIFTY Call/Put Options** & **5%+ Stock Breakouts** across the Indian Stock Market (NSE / BSE).\n\n"
        "🎯 <b>NIFTY & BANK NIFTY OPTIONS ENGINE:</b>\n"
        "• 🔮 <b>Next-Day Directional Forecast:</b> Predicts Bullish 🟢 vs Bearish 🔴 Market Move\n"
        "• 📞 <b>Option Strike Signals:</b> Precise <b>CALL (CE)</b> or <b>PUT (PE)</b> Strike Selection\n"
        "• 💰 <b>Premium Targets:</b> Entry Zone, <b>Target 1 (+40% ROI)</b>, <b>Target 2 (+80% ROI)</b>, Stop Loss (-25% Risk)\n"
        "• 🏛️ <b>FII & DII Data:</b> Tracks Foreign & Domestic Institutional Net Buying/Selling (₹ Cr)\n\n"
        "🚀 <b>EQUITY BREAKOUT ENGINE:</b>\n"
        "• <b>5%+ Daily Move Target:</b> Scans Large, Mid & Small Cap NSE/BSE Equities for 2.0x+ Volume Breakouts\n\n"
        "Tap any button below to generate instant Call/Put signals or Stock Breakouts!"
    )
    await update.message.reply_text(welcome, parse_mode="HTML", reply_markup=get_trademaster_keyboard())

async def tm_nifty_options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🔮 Studying Daily NIFTY Market Data, FII/DII Net Flows & PCR Ratio for Next-Day Forecast...")

    opt = NiftyOptionsAnalyzer.analyze_nifty_options("NIFTY")
    
    msg = (
        f"🎯 <b>NIFTY 50 OPTIONS CALL / PUT SIGNAL</b> 🎯\n"
        f"<b>Rating:</b> {opt['stars']} (<b>{opt['win_probability']} Probability</b>)\n"
        f"═════════════════════════\n"
        f"📈 <b>NEXT-DAY MARKET FORECAST:</b> <code>{opt['next_day_forecast']}</code>\n"
        f"💰 <b>NIFTY CURRENT LEVEL:</b> <code>{opt['current_level']:.2f}</code> ({opt['daily_change_pct']:+.2f}%)\n"
        f"═════════════════════════\n"
        f"📞 <b>RECOMMENDED OPTION:</b> <code>{opt['recommended_strike']}</code>\n"
        f"💵 <b>PREMIUM ENTRY ZONE:</b> <code>{opt['premium_entry']}</code>\n"
        f"🛑 <b>PREMIUM STOP LOSS:</b> <code>{opt['sl_premium']}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>{opt['target1_premium']}</code>\n"
        f"🚀 <b>TARGET 2:</b> <code>{opt['target2_premium']}</code>\n"
        f"═════════════════════════\n"
        f"🏛️ <b>INSTITUTIONAL FII/DII DRIVERS:</b>\n"
        f"• {opt['fii_dii']['summary']}\n"
        f"• <b>PCR Sentiment:</b> {opt['pcr_ratio']} ({opt['pcr_sentiment']})\n"
        f"═════════════════════════\n"
        f"💡 <i>Buy Call (CE) when next-day forecast is Bullish, Buy Put (PE) when Bearish. Move SL to Break-Even at Target 1.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_banknifty_options_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🏦 Studying Daily BANK NIFTY Market Data, FII/DII Flows & Banking Sector Technicals...")

    opt = NiftyOptionsAnalyzer.analyze_nifty_options("BANKNIFTY")
    
    msg = (
        f"🏦 <b>BANK NIFTY OPTIONS CALL / PUT SIGNAL</b> 🏦\n"
        f"<b>Rating:</b> {opt['stars']} (<b>{opt['win_probability']} Probability</b>)\n"
        f"═════════════════════════\n"
        f"📈 <b>NEXT-DAY MARKET FORECAST:</b> <code>{opt['next_day_forecast']}</code>\n"
        f"💰 <b>BANK NIFTY LEVEL:</b> <code>{opt['current_level']:.2f}</code> ({opt['daily_change_pct']:+.2f}%)\n"
        f"═════════════════════════\n"
        f"📞 <b>RECOMMENDED OPTION:</b> <code>{opt['recommended_strike']}</code>\n"
        f"💵 <b>PREMIUM ENTRY ZONE:</b> <code>{opt['premium_entry']}</code>\n"
        f"🛑 <b>PREMIUM STOP LOSS:</b> <code>{opt['sl_premium']}</code>\n"
        f"✅ <b>TARGET 1:</b> <code>{opt['target1_premium']}</code>\n"
        f"🚀 <b>TARGET 2:</b> <code>{opt['target2_premium']}</code>\n"
        f"═════════════════════════\n"
        f"🏛️ <b>INSTITUTIONAL FII/DII DRIVERS:</b>\n"
        f"• {opt['fii_dii']['summary']}\n"
        f"• <b>PCR Ratio:</b> {opt['pcr_ratio']}\n"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

async def tm_fiidii_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("📊 Fetching Daily FII & DII Net Institutional Buying/Selling Data...")

    data = NiftyOptionsAnalyzer.get_fii_dii_data()
    
    fii_icon = "🟢 Net Buyers" if data["fii_net_cr"] > 0 else "🔴 Net Sellers"
    dii_icon = "🟢 Net Buyers" if data["dii_net_cr"] > 0 else "🔴 Net Sellers"

    msg = (
        f"📊 <b>INSTITUTIONAL FII & DII FLOW RADAR</b> 📊\n"
        f"═════════════════════════\n"
        f"🌐 <b>FII (Foreign Institutional Net):</b>\n"
        f"  • Net Value: <b>{'＋' if data['fii_net_cr'] > 0 else ''}₹{data['fii_net_cr']:.2f} Cr</b> ({fii_icon})\n\n"
        f"🏛️ <b>DII (Domestic Institutional Net):</b>\n"
        f"  • Net Value: <b>{'＋' if data['dii_net_cr'] > 0 else ''}₹{data['dii_net_cr']:.2f} Cr</b> ({dii_icon})\n\n"
        f"💰 <b>TOTAL NET INSTITUTIONAL FLOW:</b>\n"
        f"  • Combined Net: <b>{'＋' if data['total_net_cr'] > 0 else ''}₹{data['total_net_cr']:.2f} Cr</b>\n"
        f"═════════════════════════\n"
        f"💡 <i>Positive FII/DII net inflows drive strong next-day NIFTY Call (CE) option rallies.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_trademaster_inline_buttons())

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
    
    if data == "tm_nifty_opt":
        await tm_nifty_options_command(update, context)
    elif data == "tm_banknifty_opt":
        await tm_banknifty_options_command(update, context)
    elif data == "tm_fiidii":
        await tm_fiidii_command(update, context)
    elif data == "tm_breakout":
        await tm_breakout_command(update, context)
    elif data == "tm_largecap":
        await tm_largecap_command(update, context)
    elif data == "tm_midcap":
        await tm_midcap_command(update, context)
    elif data == "tm_smallcap":
        await tm_smallcap_command(update, context)

async def tm_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "NIFTY Call" in text or "nifty_options" in text:
        await tm_nifty_options_command(update, context)
    elif "BANK NIFTY Call" in text:
        await tm_banknifty_options_command(update, context)
    elif "FII / DII" in text:
        await tm_fiidii_command(update, context)
    elif "Breakout" in text:
        await tm_breakout_command(update, context)
    elif "Large Cap" in text:
        await tm_largecap_command(update, context)
    elif "Mid Cap" in text:
        await tm_midcap_command(update, context)
    elif "Small Cap" in text:
        await tm_smallcap_command(update, context)
    elif "Chart" in text:
        await tm_chart_command(update, context)

async def run_trademaster_bot(token: str):
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("TradeMaster token not configured.")
        return

    logger.info("Initializing TradeMaster Options & 5%+ Breakout Bot Application...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", tm_start_command))
    app.add_handler(CommandHandler("nifty_options", tm_nifty_options_command))
    app.add_handler(CommandHandler("banknifty_options", tm_banknifty_options_command))
    app.add_handler(CommandHandler("fiidii", tm_fiidii_command))
    app.add_handler(CommandHandler("breakout", tm_breakout_command))
    app.add_handler(CommandHandler("largecap", tm_largecap_command))
    app.add_handler(CommandHandler("midcap", tm_midcap_command))
    app.add_handler(CommandHandler("smallcap", tm_smallcap_command))
    app.add_handler(CommandHandler("chart", tm_chart_command))
    app.add_handler(CallbackQueryHandler(tm_callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, tm_text_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info("🇮🇳 TradeMaster (Options & 5%+ Breakout Bot) is LIVE & listening on Telegram!")

    while True:
        await asyncio.sleep(3600)
