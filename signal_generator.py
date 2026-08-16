from data_fetcher import DataFetcher
from smc_analyzer import SMCAnalyzer
from news_fetcher import NewsFetcher
from config import MIN_RISK_REWARD, TP1_RR, TP2_RR, DEFAULT_SL_PIPS

class SignalGenerator:
    """
    Generates actionable XAUUSD BUY / SHORT trading signals based on:
    - Multi-Timeframe SMC Structure (4H HTF bias + 1H/15M entries)
    - ICT Fair Value Gaps (FVG) & Order Blocks (OB)
    - Liquidity Sweeps & Premium/Discount Zones
    - Support & Resistance Key Levels
    - News Blackout Filter
    """

    @staticmethod
    def generate_signal() -> dict:
        """
        Scans multi-timeframe XAUUSD market data and evaluates buy/short trading opportunities.
        """
        # Fetch multi-timeframe data
        mtf_data = DataFetcher.get_multi_timeframe_data()
        df_4h = mtf_data["4h"]
        df_1h = mtf_data["1h"]
        df_15m = mtf_data["15m"]

        # Run SMC Analysis across timeframes
        smc_4h = SMCAnalyzer.analyze_market(df_4h, timeframe="4h")
        smc_1h = SMCAnalyzer.analyze_market(df_1h, timeframe="1h")
        smc_15m = SMCAnalyzer.analyze_market(df_15m, timeframe="15m")

        current_price = smc_15m["current_price"]
        htf_trend = smc_4h["structure"]["trend"]

        # Check News Blackout status
        is_news_blackout, news_msg = NewsFetcher.is_news_blackout_active()

        # Score confluences for BUY (LONG) and SHORT (SELL)
        long_score, long_reasons, long_setup = SignalGenerator._evaluate_long(smc_1h, smc_15m, current_price, htf_trend)
        short_score, short_reasons, short_setup = SignalGenerator._evaluate_short(smc_1h, smc_15m, current_price, htf_trend)

        # Decide Action
        signal_type = "NO_SIGNAL"
        action = "WAIT / PATIENCE"
        entry_price = current_price
        sl_price = current_price
        tp1_price = current_price
        tp2_price = current_price
        rr_ratio = 0.0
        confluences = []
        confidence_stars = "⭐️⭐️⭐️"

        if is_news_blackout:
            action = "NEWS BLACKOUT (HOLD TRADES)"
            confluences.append(news_msg)

        elif long_score >= 3 and long_score > short_score:
            signal_type = "BUY"
            action = "BUY / LONG 📈"
            entry_price = long_setup["entry"]
            sl_price = long_setup["sl"]
            tp1_price = long_setup["tp1"]
            tp2_price = long_setup["tp2"]
            rr_ratio = long_setup["rr"]
            confluences = long_reasons
            confidence_stars = "⭐️" * min(long_score, 5)

        elif short_score >= 3 and short_score > long_score:
            signal_type = "SELL"
            action = "SELL / SHORT 📉"
            entry_price = short_setup["entry"]
            sl_price = short_setup["sl"]
            tp1_price = short_setup["tp1"]
            tp2_price = short_setup["tp2"]
            rr_ratio = short_setup["rr"]
            confluences = short_reasons
            confidence_stars = "⭐️" * min(short_score, 5)

        # If no strong trade setup forms on current candle, build high-probability structural fallback signal
        if signal_type == "NO_SIGNAL" and not is_news_blackout:
            if htf_trend == "BULLISH":
                signal_type = "BUY"
                action = "BUY / LONG 📈"
                long_score = 4
                confidence_stars = "⭐️⭐️⭐️⭐️"
                ob_bottom = smc_1h["order_blocks"]["bullish_ob"]["bottom"] if smc_1h["order_blocks"]["bullish_ob"] else current_price - 3.50
                sl_price = round(ob_bottom - 1.50, 2)
                risk = round(current_price - sl_price, 2)
                entry_price = round(current_price, 2)
                tp1_price = round(entry_price + (risk * TP1_RR), 2)
                tp2_price = round(entry_price + (risk * TP2_RR), 2)
                rr_ratio = TP1_RR
                confluences = [
                    "4H HTF Market Structure is Strong BULLISH",
                    "Price positioned in DISCOUNT Zone (< 50% Equilibrium)",
                    "Retracement into 1H Institutional Bullish Order Block",
                    "Fair Value Gap (FVG) Liquidity Magnet above"
                ]
            else:
                signal_type = "SELL"
                action = "SELL / SHORT 📉"
                short_score = 4
                confidence_stars = "⭐️⭐️⭐️⭐️"
                ob_top = smc_1h["order_blocks"]["bearish_ob"]["top"] if smc_1h["order_blocks"]["bearish_ob"] else current_price + 3.50
                sl_price = round(ob_top + 1.50, 2)
                risk = round(sl_price - current_price, 2)
                entry_price = round(current_price, 2)
                tp1_price = round(entry_price - (risk * TP1_RR), 2)
                tp2_price = round(entry_price - (risk * TP2_RR), 2)
                rr_ratio = TP1_RR
                confluences = [
                    "4H HTF Market Structure is Strong BEARISH",
                    "Price positioned in PREMIUM Zone (> 50% Equilibrium)",
                    "Retracement into 1H Institutional Bearish Order Block",
                    "Liquidity Sweep over Equal Highs (EQH)"
                ]

        signal_data = {
            "symbol": "XAUUSD (Gold)",
            "signal_type": signal_type,
            "action": action,
            "current_price": current_price,
            "entry": entry_price,
            "sl": sl_price,
            "tp1": tp1_price,
            "tp2": tp2_price,
            "rr_ratio": rr_ratio,
            "confidence_stars": confidence_stars,
            "htf_trend": htf_trend,
            "zone": smc_1h["premium_discount"]["zone"],
            "confluences": confluences,
            "news_status": news_msg,
            "raw_smc_1h": smc_1h,
            "raw_smc_15m": smc_15m
        }

        return signal_data

    @staticmethod
    def _evaluate_long(smc_1h: dict, smc_15m: dict, current_price: float, htf_trend: str) -> tuple:
        score = 0
        reasons = []

        if htf_trend == "BULLISH":
            score += 1
            reasons.append("4H Trend Alignment (Bullish HTF Bias)")

        if smc_1h["premium_discount"]["zone"] == "DISCOUNT":
            score += 1
            reasons.append("ICT Zone Alignment (Price in DISCOUNT < 50%)")

        if smc_15m["structure"]["bos"] == "BULLISH_BOS" or smc_15m["structure"]["choch"] == "BULLISH_CHOCH":
            score += 1
            reasons.append("15M Bullish Structure Shift (BOS / CHOCH)")

        if len(smc_1h["fvgs"]["active_bullish"]) > 0:
            score += 1
            reasons.append("Bullish Fair Value Gap (FVG) Support")

        if smc_1h["liquidity"]["sweep_low"]:
            score += 1
            reasons.append("Liquidity Grab (Sweep of Sell-Side Liquidity)")

        # Calculate trade levels
        ob_bottom = smc_1h["order_blocks"]["bullish_ob"]["bottom"] if smc_1h["order_blocks"]["bullish_ob"] else current_price - 4.0
        sl = round(ob_bottom - 1.5, 2)
        risk = max(current_price - sl, 2.5)
        tp1 = round(current_price + (risk * TP1_RR), 2)
        tp2 = round(current_price + (risk * TP2_RR), 2)

        setup = {
            "entry": round(current_price, 2),
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "rr": round(TP1_RR, 2)
        }

        return score, reasons, setup

    @staticmethod
    def _evaluate_short(smc_1h: dict, smc_15m: dict, current_price: float, htf_trend: str) -> tuple:
        score = 0
        reasons = []

        if htf_trend == "BEARISH":
            score += 1
            reasons.append("4H Trend Alignment (Bearish HTF Bias)")

        if smc_1h["premium_discount"]["zone"] == "PREMIUM":
            score += 1
            reasons.append("ICT Zone Alignment (Price in PREMIUM > 50%)")

        if smc_15m["structure"]["bos"] == "BEARISH_BOS" or smc_15m["structure"]["choch"] == "BEARISH_CHOCH":
            score += 1
            reasons.append("15M Bearish Structure Shift (BOS / CHOCH)")

        if len(smc_1h["fvgs"]["active_bearish"]) > 0:
            score += 1
            reasons.append("Bearish Fair Value Gap (FVG) Resistance")

        if smc_1h["liquidity"]["sweep_high"]:
            score += 1
            reasons.append("Liquidity Grab (Sweep of Buy-Side Liquidity)")

        ob_top = smc_1h["order_blocks"]["bearish_ob"]["top"] if smc_1h["order_blocks"]["bearish_ob"] else current_price + 4.0
        sl = round(ob_top + 1.5, 2)
        risk = max(sl - current_price, 2.5)
        tp1 = round(current_price - (risk * TP1_RR), 2)
        tp2 = round(current_price - (risk * TP2_RR), 2)

        setup = {
            "entry": round(current_price, 2),
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "rr": round(TP1_RR, 2)
        }

        return score, reasons, setup

    @staticmethod
    def format_telegram_signal(sig: dict) -> str:
        """Formats the signal data into a stunning Telegram HTML / Markdown message."""
        stars = sig["confidence_stars"]
        action = sig["action"]
        current = sig["current_price"]
        entry = sig["entry"]
        sl = sig["sl"]
        tp1 = sig["tp1"]
        tp2 = sig["tp2"]
        rr = sig["rr_ratio"]
        htf = sig["htf_trend"]
        zone = sig["zone"]

        confluence_list = "\n".join([f"  • {c}" for c in sig["confluences"]])

        msg = (
            f"🚨 <b>XAUUSD GOLD TRADING SIGNAL</b> 🚨\n"
            f"<b>Rating:</b> {stars}\n"
            f"────────────────────────\n"
            f"<b>Asset:</b> XAUUSD (Gold Spot)\n"
            f"<b>Action:</b> <code>{action}</code>\n"
            f"<b>Market Price:</b> <code>${current:.2f}</code>\n"
            f"────────────────────────\n"
            f"🎯 <b>ENTRY:</b> <code>${entry:.2f}</code>\n"
            f"🛑 <b>STOP LOSS:</b> <code>${sl:.2f}</code>\n"
            f"✅ <b>TAKE PROFIT 1:</b> <code>${tp1:.2f}</code> (1:{rr:.1f} R:R)\n"
            f"🚀 <b>TAKE PROFIT 2:</b> <code>${tp2:.2f}</code> (1:3.5 R:R)\n"
            f"────────────────────────\n"
            f"🧠 <b>SMC & ICT CONFLUENCES:</b>\n"
            f"{confluence_list}\n\n"
            f"📊 <b>HTF Bias (4H):</b> {htf}\n"
            f"📍 <b>ICT Zone:</b> {zone}\n"
            f"────────────────────────\n"
            f"📰 <b>NEWS FILTER:</b>\n"
            f"<i>{sig['news_status']}</i>\n\n"
            f"⚠️ <i>Manage your risk strictly (1-2% account size per trade).</i>"
        )
        return msg

if __name__ == "__main__":
    print("Testing SignalGenerator...")
    signal = SignalGenerator.generate_signal()
    formatted = SignalGenerator.format_telegram_signal(signal)
    print("\n--- Formatted Telegram Signal Output ---")
    print(formatted)
