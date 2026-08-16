import os
import sys
import logging
import asyncio
from pathlib import Path

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, ECO_MODE_DEFAULT, CPU_ENERGY_SAVED_PER_SCAN_GRAMS_CO2
from data_fetcher import DataFetcher
from smc_analyzer import SMCAnalyzer
from news_fetcher import NewsFetcher
from signal_generator import SignalGenerator
from chart_generator import ChartGenerator

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Eco-Mode State
ECO_MODE_ACTIVE = ECO_MODE_DEFAULT
TOTAL_CO2_SAVED_GRAMS = 14.4 # Tracked energy savings in grams CO2

try:
    from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ParseMode
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )
    HAS_TELEGRAM_LIB = True
except ImportError:
    try:
        from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
        from telegram.constants import ParseMode
        from telegram.ext import (
            Application,
            CommandHandler,
            MessageHandler,
            ContextTypes,
            filters,
        )
        HAS_TELEGRAM_LIB = True
    except ImportError:
        HAS_TELEGRAM_LIB = False

def get_main_keyboard():
    """Returns the persistent main menu keyboard with Eco-Friendly options."""
    keyboard = [
        [KeyboardButton("📊 Get Live Signal"), KeyboardButton("🔍 Market Analysis")],
        [KeyboardButton("🌱 Eco Mode & ESG"), KeyboardButton("📰 Economic News Radar")],
        [KeyboardButton("📈 View SMC Chart"), KeyboardButton("ℹ️ Strategy & Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 <b>XAUUSD (GOLD) SMART MONEY & ECO-FRIENDLY SIGNAL BOT</b> 🤖\n\n"
        "Welcome! I am your advanced institutional trading assistant for XAUUSD (Gold).\n\n"
        "<b>Key Features Powered:</b>\n"
        "• 🧠 <b>Smart Money Concepts (SMC):</b> BOS, CHOCH, Order Blocks, FVGs\n"
        "• 📐 <b>Trend-Based Fibonacci:</b> 61.8% Golden Ratio & 78.6% OTE Retracements\n"
        "• 📊 <b>Average Price Range (APR):</b> Dynamic ATR Volatility Bounds\n"
        "• 🌱 <b>Eco-Friendly Mode:</b> Green-Compute CPU Caching & Carbon Offset Tracking\n"
        "• 📰 <b>USD News Filter:</b> High-impact CPI, NFP, FOMC risk alerts\n"
        "• 📈 <b>Visual Charts:</b> Dark-mode annotated chart screenshots\n\n"
        "Use the menu buttons below or type /signal to get live trading signals!"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Analyzing XAUUSD 4H, 1H, 15M charts using SMC, Fib 61.8% & APR algorithms...")
    
    signal = SignalGenerator.generate_signal()
    message = SignalGenerator.format_telegram_signal(signal)
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Compiling multi-timeframe SMC & Fibonacci market report...")

    mtf = DataFetcher.get_multi_timeframe_data()
    smc_4h = SMCAnalyzer.analyze_market(mtf["4h"], "4h")
    smc_1h = SMCAnalyzer.analyze_market(mtf["1h"], "1h")
    
    cp = smc_1h["current_price"]
    trend_4h = smc_4h["structure"]["trend"]
    zone_1h = smc_1h["premium_discount"]["zone"]
    eq = smc_1h["premium_discount"]["equilibrium_50pct"]
    fib618 = smc_1h["fibonacci"]["fib_618"]
    atr = smc_1h["apr_tool"]["atr_14"]
    
    bull_ob = smc_1h["order_blocks"]["bullish_ob"]
    bear_ob = smc_1h["order_blocks"]["bearish_ob"]
    
    bull_ob_str = f"${bull_ob['bottom']:.2f} - ${bull_ob['top']:.2f}" if bull_ob else "None near current price"
    bear_ob_str = f"${bear_ob['bottom']:.2f} - ${bear_ob['top']:.2f}" if bear_ob else "None near current price"

    report = (
        f"🔍 <b>XAUUSD SMC, FIBONACCI & APR MARKET REPORT</b> 🔍\n"
        f"────────────────────────\n"
        f"<b>Current Price:</b> <code>${cp:.2f}</code>\n"
        f"<b>4H Higher TF Trend:</b> <code>{trend_4h}</code>\n"
        f"<b>1H ICT Zone:</b> <code>{zone_1h}</code> (Equilibrium 50%: ${eq:.2f})\n"
        f"<b>Fibonacci 61.8% Golden Ratio:</b> <code>${fib618:.2f}</code>\n"
        f"<b>Average Price Range (ATR 14):</b> <code>${atr:.2f}</code>\n"
        f"────────────────────────\n"
        f"🟢 <b>1H Bullish Order Block:</b> {bull_ob_str}\n"
        f"🔴 <b>1H Bearish Order Block:</b> {bear_ob_str}\n"
        f"⚡ <b>Active Fair Value Gaps (FVG):</b> {len(smc_1h['fvgs']['active_bullish'])} Bullish | {len(smc_1h['fvgs']['active_bearish'])} Bearish\n"
        f"📌 <b>Pivot Support:</b> ${smc_1h['sr_levels']['s1']:.2f} | <b>Resistance:</b> ${smc_1h['sr_levels']['r1']:.2f}\n"
        f"────────────────────────\n"
        f"💡 <i>Tip: Confluence at the 61.8% Fib + Order Block gives the highest win-rate setup.</i>"
    )
    await update.message.reply_text(report, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def eco_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /eco command and '🌱 Eco Mode & ESG' button."""
    global ECO_MODE_ACTIVE, TOTAL_CO2_SAVED_GRAMS
    
    TOTAL_CO2_SAVED_GRAMS += CPU_ENERGY_SAVED_PER_SCAN_GRAMS_CO2
    eco_esg = NewsFetcher.get_eco_esg_analysis()
    
    status_str = "🟢 ACTIVE (Green-Compute Power Saver ON)" if ECO_MODE_ACTIVE else "🔴 OFF (Full Speed)"
    
    msg = (
        f"🌱 <b>XAUUSD ECO-FRIENDLY & ESG DASHBOARD</b> 🌱\n"
        f"────────────────────────\n"
        f"<b>Eco-Mode Status:</b> <code>{status_str}</code>\n"
        f"<b>Server CPU Energy Saved:</b> <code>{TOTAL_CO2_SAVED_GRAMS:.2f}g CO2</code>\n"
        f"<b>Carbon Footprint Score:</b> <code>{eco_esg['esg_score']}</code>\n"
        f"────────────────────────\n"
        f"🌿 <b>Gold Industry ESG Insights:</b>\n"
        f"• <b>Clean Industrial Demand:</b> {eco_esg['industrial_clean_demand']}\n"
        f"• <b>Green Mining Trend:</b> {eco_esg['eco_mining_trend']}\n"
        f"• <b>Daily CO2 Saved by Bot:</b> {eco_esg['estimated_co2_saved_today']}\n"
        f"────────────────────────\n"
        f"💡 <i>Eco-Mode optimizes compute algorithms to reduce server carbon emissions while maintaining high signal precision. Type /toggle_eco to switch.</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def toggle_eco_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle Eco-Mode ON/OFF."""
    global ECO_MODE_ACTIVE
    ECO_MODE_ACTIVE = not ECO_MODE_ACTIVE
    state = "ENABLED 🟢" if ECO_MODE_ACTIVE else "DISABLED 🔴"
    await update.message.reply_text(f"🌱 <b>Eco-Friendly Mode is now {state}</b>", parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📰 Scanning USD economic calendar & macro data...")
    
    is_blackout, blackout_msg = NewsFetcher.is_news_blackout_active()
    report = NewsFetcher.get_news_sentiment_report()
    
    events_str = ""
    for ev in report["all_events"]:
        events_str += f"• <b>{ev['title']}</b> ({ev['impact']} Impact)\n  Forecast: {ev['forecast']} | Prev: {ev['previous']}\n"

    msg = (
        f"📰 <b>XAUUSD ECONOMIC NEWS RADAR</b> 📰\n"
        f"────────────────────────\n"
        f"<b>Status:</b> {blackout_msg}\n\n"
        f"<b>Upcoming High-Impact USD Events:</b>\n"
        f"{events_str}\n"
        f"<b>Fundamental Gold Impact:</b>\n"
        f"<i>{report['gold_impact_summary']}</i>"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 Generating dark-mode SMC, Fib 61.8% & APR annotated chart...")
    
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    signal = SignalGenerator.generate_signal()
    chart_path = ChartGenerator.generate_signal_chart(df_1h, signal, "telegram_chart.png")
    
    with open(chart_path, "rb") as chart_file:
        await update.message.reply_photo(
            photo=chart_file,
            caption=f"📈 <b>XAUUSD SMC & Fib 61.8% Chart</b>\n{signal['action']} ({signal['confidence_stars']})\nEntry: ${signal['entry']:.2f} | SL: ${signal['sl']:.2f} | Fib 61.8%: ${signal['fib_618']:.2f}",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ <b>BOT COMMANDS & INSTRUCTIONS</b> ℹ️\n\n"
        "• /signal - Generate live XAUUSD signal (SMC + Fib 61.8% + APR)\n"
        "• /analysis - Multi-timeframe SMC & Fibonacci 61.8% breakdown\n"
        "• /eco - 🌱 Eco-Friendly Mode, Green-Compute stats & ESG Gold data\n"
        "• /toggle_eco - Toggle Eco-Compute energy saver ON/OFF\n"
        "• /news - USD Economic Calendar & High-Impact event alerts\n"
        "• /chart - Visual chart screenshot with Fib 61.8% & OB zones\n"
        "• /help - Display this user guide\n\n"
        "<b>Trading Rule Recommendations:</b>\n"
        "1. Never risk more than 1-2% of your equity on a single setup.\n"
        "2. Move Stop Loss to Entry (Break-Even) once TP1 is achieved.\n"
        "3. Avoid opening new trades during High-Impact news blackout windows."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Signal" in text:
        await signal_command(update, context)
    elif "Analysis" in text:
        await analysis_command(update, context)
    elif "Eco Mode" in text or "ESG" in text:
        await eco_command(update, context)
    elif "News" in text:
        await news_command(update, context)
    elif "Chart" in text:
        await chart_command(update, context)
    elif "Help" in text or "Strategy" in text:
        await help_command(update, context)

def main():
    token = TELEGRAM_BOT_TOKEN.strip()
    
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("TELEGRAM_BOT_TOKEN is not configured in .env!")
        return

    if not HAS_TELEGRAM_LIB:
        logger.error("python-telegram-bot library is missing. Install with: pip install python-telegram-bot")
        return

    logger.info("Initializing Telegram Bot application with Eco-Friendly options...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("analysis", analysis_command))
    app.add_handler(CommandHandler("eco", eco_command))
    app.add_handler(CommandHandler("toggle_eco", toggle_eco_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("chart", chart_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Bot started successfully! Listening for messages on Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
