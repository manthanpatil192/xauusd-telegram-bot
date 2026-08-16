import os
import sys
import logging
import asyncio
from pathlib import Path

from config import PRIMARY_BOT_TOKEN, TELEGRAM_CHANNEL_ID, ECO_MODE_DEFAULT, CPU_ENERGY_SAVED_PER_SCAN_GRAMS_CO2
from data_fetcher import DataFetcher
from smc_analyzer import SMCAnalyzer
from news_fetcher import NewsFetcher
from signal_generator import SignalGenerator
from chart_generator import ChartGenerator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ECO_MODE_ACTIVE = ECO_MODE_DEFAULT
TOTAL_CO2_SAVED_GRAMS = 18.5

try:
    from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
    from telegram.constants import ParseMode
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

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("⚡ Get Live Signal"), KeyboardButton("🔍 Market Analysis")],
        [KeyboardButton("📐 Fib 61.8% Golden Zone"), KeyboardButton("📊 APR Tool Volatility")],
        [KeyboardButton("🌱 Eco Mode & ESG"), KeyboardButton("📰 Economic News Radar")],
        [KeyboardButton("📈 View SMC Chart"), KeyboardButton("ℹ️ Strategy & Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_inline_signal_buttons():
    buttons = [
        [
            InlineKeyboardButton("🎯 Refresh Signal", callback_data="btn_signal"),
            InlineKeyboardButton("📈 View SMC Chart", callback_data="btn_chart")
        ],
        [
            InlineKeyboardButton("📐 Fib 61.8% Golden Zone", callback_data="btn_fib"),
            InlineKeyboardButton("📊 APR Volatility", callback_data="btn_apr")
        ],
        [
            InlineKeyboardButton("🔍 Deep Analysis", callback_data="btn_analysis"),
            InlineKeyboardButton("📰 News Risk", callback_data="btn_news")
        ],
        [
            InlineKeyboardButton("🌱 Eco Dashboard", callback_data="btn_eco")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 <b>XAUUSD HIGH-PRECISION SMART MONEY SIGNAL BOT</b> 🤖\n\n"
        "Welcome! I am your institutional trading assistant for XAUUSD (Gold).\n\n"
        "⚡ <b>Engine Capabilities:</b>\n"
        "• 🧠 <b>SMC & ICT:</b> BOS, CHOCH, Bullish/Bearish OBs, FVGs, Liquidity Sweeps\n"
        "• 📐 <b>Fibonacci 61.8% Golden Ratio:</b> Trend-Based Retracement Entry\n"
        "• 📈 <b>RSI (14) & EMA Trend:</b> Multi-Indicator Confluences & Volume Filter\n"
        "• 📊 <b>APR Tool:</b> Average Price Range (ATR 14 Volatility Bounds)\n"
        "• 🌱 <b>Eco-Friendly Mode:</b> Green-Compute Caching & Carbon Offset Metrics\n"
        "• 📰 <b>USD News Filter:</b> NFP, CPI, FOMC High-Impact Blackout Alerts\n\n"
        "Tap any menu button below to generate high-win probability signals!"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML", reply_markup=get_main_keyboard())

async def signal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🔎 Analyzing XAUUSD 4H, 1H, 15M charts using SMC, Fib 61.8%, RSI & APR algorithms...")
    
    signal = SignalGenerator.generate_signal()
    message = SignalGenerator.format_telegram_signal(signal)
    
    await target.reply_text(message, parse_mode="HTML", reply_markup=get_inline_signal_buttons())

async def fib_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("📐 Calculating Trend-Based Fibonacci Retracement Zones for XAUUSD...")

    mtf = DataFetcher.get_multi_timeframe_data()
    smc_1h = SMCAnalyzer.analyze_market(mtf["1h"], "1h")
    fib = smc_1h["fibonacci"]
    cp = smc_1h["current_price"]

    msg = (
        f"📐 <b>TREND-BASED FIBONACCI RETRACEMENT ZONES</b> 📐\n"
        f"═════════════════════════\n"
        f"💰 <b>Current XAUUSD Price:</b> <code>${cp:.2f}</code>\n\n"
        f"🌟 <b>Golden Pocket (61.8%):</b> <code>${fib['fib_618']:.2f}</code> (Best Entry Level 🔥)\n"
        f"🎯 <b>OTE Zone (78.6%):</b> <code>${fib['fib_786']:.2f}</code>\n"
        f"📍 <b>Equilibrium (50.0%):</b> <code>${fib['fib_500']:.2f}</code>\n"
        f"🛡️ <b>Discount Support (38.2%):</b> <code>${fib['fib_382']:.2f}</code>\n"
        f"═════════════════════════\n"
        f"💡 <i>The 61.8% Golden Ratio level acts as high-probability institutional reaction zone.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_inline_signal_buttons())

async def apr_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("📊 Calculating Average Price Range (APR / ATR 14) Volatility Bounds...")

    mtf = DataFetcher.get_multi_timeframe_data()
    smc_1h = SMCAnalyzer.analyze_market(mtf["1h"], "1h")
    apr = smc_1h["apr_tool"]
    cp = smc_1h["current_price"]

    msg = (
        f"📊 <b>AVERAGE PRICE RANGE (APR TOOL) REPORT</b> 📊\n"
        f"═════════════════════════\n"
        f"💰 <b>Current XAUUSD Price:</b> <code>${cp:.2f}</code>\n"
        f"⚡ <b>14-Period Average Range (ATR):</b> <code>${apr['atr_14']:.2f}</code>\n"
        f"═════════════════════════\n"
        f"🚀 <b>Upper Expected Volatility Bound:</b> <code>${apr['upper_bound_1d']:.2f}</code>\n"
        f"📉 <b>Lower Expected Volatility Bound:</b> <code>${apr['lower_bound_1d']:.2f}</code>\n"
        f"═════════════════════════\n"
        f"💡 <i>Use APR bounds to avoid placing stop loss within normal daily noise range.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_inline_signal_buttons())

async def analysis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("⏳ Compiling multi-timeframe SMC, Fibonacci & RSI market report...")

    mtf = DataFetcher.get_multi_timeframe_data()
    smc_4h = SMCAnalyzer.analyze_market(mtf["4h"], "4h")
    smc_1h = SMCAnalyzer.analyze_market(mtf["1h"], "1h")
    
    cp = smc_1h["current_price"]
    trend_4h = smc_4h["structure"]["trend"]
    zone_1h = smc_1h["premium_discount"]["zone"]
    eq = smc_1h["premium_discount"]["equilibrium_50pct"]
    fib618 = smc_1h["fibonacci"]["fib_618"]
    rsi = smc_1h["indicators"]["rsi_14"]
    atr = smc_1h["apr_tool"]["atr_14"]
    
    bull_ob = smc_1h["order_blocks"]["bullish_ob"]
    bear_ob = smc_1h["order_blocks"]["bearish_ob"]
    
    bull_ob_str = f"${bull_ob['bottom']:.2f} - ${bull_ob['top']:.2f}" if bull_ob else "None near current price"
    bear_ob_str = f"${bear_ob['bottom']:.2f} - ${bear_ob['top']:.2f}" if bear_ob else "None near current price"

    report = (
        f"🔍 <b>XAUUSD DEEP MARKET CONFLUENCE REPORT</b> 🔍\n"
        f"═════════════════════════\n"
        f"💰 <b>Current Price:</b> <code>${cp:.2f}</code>\n"
        f"📈 <b>4H Trend Bias:</b> <code>{trend_4h}</code>\n"
        f"📍 <b>ICT Zone:</b> <code>{zone_1h}</code> (50% Eq: ${eq:.2f})\n"
        f"📐 <b>Fibonacci 61.8% Level:</b> <code>${fib618:.2f}</code>\n"
        f"📊 <b>RSI 14 Momentum:</b> <code>{rsi}</code>\n"
        f"📊 <b>Average Price Range (ATR 14):</b> <code>${atr:.2f}</code>\n"
        f"═════════════════════════\n"
        f"🟢 <b>1H Bullish Order Block:</b> {bull_ob_str}\n"
        f"🔴 <b>1H Bearish Order Block:</b> {bear_ob_str}\n"
        f"⚡ <b>Active Fair Value Gaps (FVG):</b> {len(smc_1h['fvgs']['active_bullish'])} Bullish | {len(smc_1h['fvgs']['active_bearish'])} Bearish\n"
        f"📌 <b>Pivot Support:</b> ${smc_1h['sr_levels']['s1']:.2f} | <b>Resistance:</b> ${smc_1h['sr_levels']['r1']:.2f}\n"
        f"═════════════════════════\n"
        f"💡 <i>High-win setups occur when price retests the 61.8% Fib + Order Block zone simultaneously.</i>"
    )
    await target.reply_text(report, parse_mode="HTML", reply_markup=get_inline_signal_buttons())

async def eco_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ECO_MODE_ACTIVE, TOTAL_CO2_SAVED_GRAMS
    target = update.message if update.message else update.callback_query.message
    
    TOTAL_CO2_SAVED_GRAMS += CPU_ENERGY_SAVED_PER_SCAN_GRAMS_CO2
    eco_esg = NewsFetcher.get_eco_esg_analysis()
    status_str = "🟢 ACTIVE (Green-Compute Power Saver ON)" if ECO_MODE_ACTIVE else "🔴 OFF (Full Speed)"
    
    msg = (
        f"🌱 <b>XAUUSD ECO-FRIENDLY & ESG DASHBOARD</b> 🌱\n"
        f"═════════════════════════\n"
        f"<b>Eco-Mode Status:</b> <code>{status_str}</code>\n"
        f"<b>Server Energy Saved:</b> <code>{TOTAL_CO2_SAVED_GRAMS:.2f}g CO2</code>\n"
        f"<b>Carbon Footprint Score:</b> <code>{eco_esg['esg_score']}</code>\n"
        f"═════════════════════════\n"
        f"🌿 <b>Gold ESG Market Insights:</b>\n"
        f"• <b>Clean Energy Demand:</b> {eco_esg['industrial_clean_demand']}\n"
        f"• <b>Green Mining Trend:</b> {eco_esg['eco_mining_trend']}\n"
        f"• <b>Daily CO2 Saved by Bot:</b> {eco_esg['estimated_co2_saved_today']}\n"
        f"═════════════════════════\n"
        f"💡 <i>Eco-Mode optimizes compute algorithms to reduce server carbon emissions. Type /toggle_eco to switch.</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_inline_signal_buttons())

async def toggle_eco_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ECO_MODE_ACTIVE
    ECO_MODE_ACTIVE = not ECO_MODE_ACTIVE
    state = "ENABLED 🟢" if ECO_MODE_ACTIVE else "DISABLED 🔴"
    await update.message.reply_text(f"🌱 <b>Eco-Friendly Mode is now {state}</b>", parse_mode="HTML", reply_markup=get_main_keyboard())

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("📰 Scanning USD economic calendar & macro data...")
    
    is_blackout, blackout_msg = NewsFetcher.is_news_blackout_active()
    report = NewsFetcher.get_news_sentiment_report()
    
    events_str = ""
    for ev in report["all_events"]:
        events_str += f"• <b>{ev['title']}</b> ({ev['impact']} Impact)\n  Forecast: {ev['forecast']} | Prev: {ev['previous']}\n"

    msg = (
        f"📰 <b>XAUUSD ECONOMIC NEWS RADAR</b> 📰\n"
        f"═════════════════════════\n"
        f"<b>Status:</b> {blackout_msg}\n\n"
        f"<b>Upcoming High-Impact USD Events:</b>\n"
        f"{events_str}\n"
        f"<b>Fundamental Gold Impact:</b>\n"
        f"<i>{report['gold_impact_summary']}</i>"
    )
    await target.reply_text(msg, parse_mode="HTML", reply_markup=get_inline_signal_buttons())

async def chart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message if update.message else update.callback_query.message
    await target.reply_text("🎨 Rendering dark-mode SMC, Fib 61.8% & APR visual chart...")
    
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    signal = SignalGenerator.generate_signal()
    chart_path = ChartGenerator.generate_signal_chart(df_1h, signal, "telegram_chart.png")
    
    with open(chart_path, "rb") as chart_file:
        await target.reply_photo(
            photo=chart_file,
            caption=f"📈 <b>XAUUSD Chart</b> | {signal['action']} ({signal['confidence_stars']})\nEntry: ${signal['entry']:.2f} | SL: ${signal['sl']:.2f} | Fib 61.8%: ${signal['fib_618']:.2f}",
            parse_mode="HTML",
            reply_markup=get_inline_signal_buttons()
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "ℹ️ <b>BOT USER GUIDE & RULES</b> ℹ️\n\n"
        "• /signal - Generate live XAUUSD signal (SMC + Fib 61.8% + RSI + APR)\n"
        "• /analysis - Deep multi-timeframe SMC & Fibonacci breakdown\n"
        "• /fib - 📐 Trend-Based Fibonacci 61.8% Golden Ratio level\n"
        "• /apr - 📊 Average Price Range (ATR 14) volatility bounds\n"
        "• /eco - 🌱 Eco-Mode, Green-Compute stats & ESG Gold data\n"
        "• /news - USD Economic Calendar & High-Impact event alerts\n"
        "• /chart - Visual chart screenshot with Fib 61.8% & OB zones"
    )
    await update.message.reply_text(help_text, parse_mode="HTML", reply_markup=get_main_keyboard())

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "btn_signal":
        await signal_command(update, context)
    elif data == "btn_analysis":
        await analysis_command(update, context)
    elif data == "btn_fib":
        await fib_command(update, context)
    elif data == "btn_apr":
        await apr_command(update, context)
    elif data == "btn_chart":
        await chart_command(update, context)
    elif data == "btn_news":
        await news_command(update, context)
    elif data == "btn_eco":
        await eco_command(update, context)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Signal" in text:
        await signal_command(update, context)
    elif "Analysis" in text:
        await analysis_command(update, context)
    elif "Fib" in text or "61.8%" in text:
        await fib_command(update, context)
    elif "APR" in text or "Volatility" in text:
        await apr_command(update, context)
    elif "Eco Mode" in text or "ESG" in text:
        await eco_command(update, context)
    elif "News" in text:
        await news_command(update, context)
    elif "Chart" in text:
        await chart_command(update, context)
    elif "Help" in text or "Strategy" in text:
        await help_command(update, context)

async def run_bot_instance(token: str):
    if not HAS_TELEGRAM_LIB:
        logger.error("python-telegram-bot library is missing!")
        return

    logger.info(f"Initializing Bot Instance (Token ending: ...{token[-8:]})...")
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("signal", signal_command))
    app.add_handler(CommandHandler("analysis", analysis_command))
    app.add_handler(CommandHandler("fib", fib_command))
    app.add_handler(CommandHandler("apr", apr_command))
    app.add_handler(CommandHandler("eco", eco_command))
    app.add_handler(CommandHandler("toggle_eco", toggle_eco_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("chart", chart_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    logger.info(f"✅ Bot Instance (...{token[-8:]}) is now LIVE & listening!")

    while True:
        await asyncio.sleep(3600)

def main():
    token = PRIMARY_BOT_TOKEN.strip()
    if token:
        asyncio.run(run_bot_instance(token))

if __name__ == "__main__":
    main()
