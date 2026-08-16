import os
import sys
import logging
import asyncio
from pathlib import Path

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
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

# Import python-telegram-bot modules
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
    """Returns the persistent main menu keyboard for Telegram chat."""
    keyboard = [
        [KeyboardButton("📊 Get Live Signal"), KeyboardButton("🔍 Market Analysis")],
        [KeyboardButton("📰 Economic News Radar"), KeyboardButton("📈 View SMC Chart")],
        [KeyboardButton("ℹ️ Strategy & Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    welcome_text = (
        "🤖 <b>XAUUSD (GOLD) SMART MONEY & ICT SIGNAL BOT</b> 🤖\n\n"
        "Welcome! I am your advanced institutional trading assistant for XAUUSD (Gold).\n\n"
        "<b>Key Features Powered:</b>\n"
        "• 🧠 <b>Smart Money Concepts (SMC):</b> BOS, CHOCH, Order Blocks, FVGs\n"
        "• 🎯 <b>ICT Methodology:</b> Liquidity Sweeps, Premium/Discount 50% Equilibrium\n"
        "• 📍 <b>Support & Resistance:</b> Pivots, PDH/PDL Levels\n"
        "• 📰 <b>USD News Filter:</b> High-impact CPI, NFP, FOMC risk alerts\n"
        "• 📈 <b>Visual Charts:</b> Annotated Entry, SL, TP chart screenshots\n\n"
        "Use the menu buttons below or type /signal to get live trading signals!"
    )
    await update.message.reply_text(welcome_text, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /signal command and '📊 Get Live Signal' button."""
    await update.message.reply_text("🔎 Analyzing XAUUSD 4H, 1H, and 15M charts using SMC & ICT algorithms...")
    
    signal = SignalGenerator.generate_signal()
    message = SignalGenerator.format_telegram_signal(signal)
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /analysis command and '🔍 Market Analysis' button."""
    await update.message.reply_text("⏳ Compiling multi-timeframe SMC market report...")

    mtf = DataFetcher.get_multi_timeframe_data()
    smc_4h = SMCAnalyzer.analyze_market(mtf["4h"], "4h")
    smc_1h = SMCAnalyzer.analyze_market(mtf["1h"], "1h")
    
    cp = smc_1h["current_price"]
    trend_4h = smc_4h["structure"]["trend"]
    zone_1h = smc_1h["premium_discount"]["zone"]
    eq = smc_1h["premium_discount"]["equilibrium_50pct"]
    
    bull_ob = smc_1h["order_blocks"]["bullish_ob"]
    bear_ob = smc_1h["order_blocks"]["bearish_ob"]
    
    bull_ob_str = f"${bull_ob['bottom']:.2f} - ${bull_ob['top']:.2f}" if bull_ob else "None near current price"
    bear_ob_str = f"${bear_ob['bottom']:.2f} - ${bear_ob['top']:.2f}" if bear_ob else "None near current price"

    report = (
        f"🔍 <b>XAUUSD SMC MARKET ANALYSIS</b> 🔍\n"
        f"────────────────────────\n"
        f"<b>Current Price:</b> <code>${cp:.2f}</code>\n"
        f"<b>4H Higher TF Trend:</b> <code>{trend_4h}</code>\n"
        f"<b>1H ICT Zone:</b> <code>{zone_1h}</code> (Equilibrium 50%: ${eq:.2f})\n"
        f"────────────────────────\n"
        f"🟢 <b>1H Bullish Order Block:</b> {bull_ob_str}\n"
        f"🔴 <b>1H Bearish Order Block:</b> {bear_ob_str}\n"
        f"⚡ <b>Active Fair Value Gaps (FVG):</b> {len(smc_1h['fvgs']['active_bullish'])} Bullish | {len(smc_1h['fvgs']['active_bearish'])} Bearish\n"
        f"📌 <b>Pivot Support:</b> ${smc_1h['sr_levels']['s1']:.2f}\n"
        f"📌 <b>Pivot Resistance:</b> ${smc_1h['sr_levels']['r1']:.2f}\n"
        f"────────────────────────\n"
        f"💡 <i>Tip: Trade in alignment with the 4H trend bias when price enters your 1H OB/FVG zones.</i>"
    )
    await update.message.reply_text(report, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /news command and '📰 Economic News Radar' button."""
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
    """Handle /chart command and '📈 View SMC Chart' button."""
    await update.message.reply_text("🎨 Generating dark-mode SMC annotated chart...")
    
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    signal = SignalGenerator.generate_signal()
    chart_path = ChartGenerator.generate_signal_chart(df_1h, signal, "telegram_chart.png")
    
    with open(chart_path, "rb") as chart_file:
        await update.message.reply_photo(
            photo=chart_file,
            caption=f"📈 <b>XAUUSD Annotated Chart</b>\n{signal['action']} ({signal['confidence_stars']})\nEntry: ${signal['entry']:.2f} | SL: ${signal['sl']:.2f} | TP1: ${signal['tp1']:.2f}",
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard()
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "ℹ️ <b>BOT COMMANDS & INSTRUCTIONS</b> ℹ️\n\n"
        "• /signal - Generate live XAUUSD signal with Entry, SL, TP1, TP2\n"
        "• /analysis - Deep multi-timeframe SMC breakdown\n"
        "• /news - USD Economic Calendar & High-Impact event alerts\n"
        "• /chart - Visual chart screenshot with marked zones\n"
        "• /help - Display this user guide\n\n"
        "<b>Trading Rule Recommendations:</b>\n"
        "1. Never risk more than 1-2% of your equity on a single setup.\n"
        "2. Move Stop Loss to Entry (Break-Even) once TP1 is achieved.\n"
        "3. Avoid opening new trades during High-Impact news blackout windows."
    )
    await update.message.reply_text(help_text, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle custom keyboard button presses."""
    text = update.message.text
    if "Signal" in text:
        await signal_command(update, context)
    elif "Analysis" in text:
        await analysis_command(update, context)
    elif "News" in text:
        await news_command(update, context)
    elif "Chart" in text:
        await chart_command(update, context)
    elif "Help" in text or "Strategy" in text:
        await help_command(update, context)

def run_cli_test_mode():
    """Runs interactive command line interface when no Telegram token is provided."""
    print("=" * 65)
    print(" 🤖 XAUUSD SMC & ICT TRADING SIGNAL BOT (CLI DEMO & TEST MODE) 🤖")
    print("=" * 65)
    print("No valid TELEGRAM_BOT_TOKEN found in .env configuration.")
    print("Running local simulation & test mode...\n")

    while True:
        print("\nChoose an option:")
        print(" [1] Generate Live Signal (/signal)")
        print(" [2] View SMC Market Analysis (/analysis)")
        print(" [3] Check Economic News Radar (/news)")
        print(" [4] Render Dark-Mode Annotated Chart PNG (/chart)")
        print(" [5] Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            print("\nGenerating Signal...")
            sig = SignalGenerator.generate_signal()
            print(SignalGenerator.format_telegram_signal(sig).replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "").replace("<i>", "").replace("</i>", ""))
        elif choice == "2":
            print("\nRunning Analysis...")
            mtf = DataFetcher.get_multi_timeframe_data()
            smc_1h = SMCAnalyzer.analyze_market(mtf["1h"], "1h")
            print(f"Current Price: ${smc_1h['current_price']:.2f}")
            print(f"Structure Trend: {smc_1h['structure']['trend']}")
            print(f"ICT Zone: {smc_1h['premium_discount']['zone']}")
        elif choice == "3":
            print("\nFetching News...")
            blackout, msg = NewsFetcher.is_news_blackout_active()
            print(f"News Status: {msg}")
        elif choice == "4":
            print("\nRendering Chart PNG...")
            df = DataFetcher.fetch_ohlcv(interval="1h")
            sig = SignalGenerator.generate_signal()
            path = ChartGenerator.generate_signal_chart(df, sig, "xauusd_chart_demo.png")
            print(f"✅ Chart saved to: {path}")
        elif choice == "5":
            print("Exiting test mode.")
            break
        else:
            print("Invalid selection.")

def main():
    """Start Telegram Bot application."""
    token = TELEGRAM_BOT_TOKEN.strip()
    
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("TELEGRAM_BOT_TOKEN is not configured in .env!")
        run_cli_test_mode()
        return

    if not HAS_TELEGRAM_LIB:
        logger.error("python-telegram-bot library is missing. Install with: pip install python-telegram-bot")
        return

    logger.info("Initializing Telegram Bot application...")
    app = Application.builder().token(token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("analysis", analysis_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("chart", chart_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("Bot started successfully! Listening for messages on Telegram...")
    app.run_polling()

if __name__ == "__main__":
    main()
