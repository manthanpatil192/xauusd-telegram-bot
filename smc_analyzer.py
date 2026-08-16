import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from config import FVG_THRESHOLD_PERCENT, OB_SWING_LOOKBACK, PREMIUM_DISCOUNT_EQUILIBRIUM

class SMCAnalyzer:
    """
    Core High-Precision Trading Engine.
    Combines:
      - Smart Money Concepts (BOS, CHOCH, Bullish/Bearish Order Blocks, FVG)
      - ICT Liquidity Sweeps & Premium/Discount 50% Equilibrium
      - Trend-Based Fibonacci Retracement (61.8% Golden Pocket & 78.6% OTE)
      - Technical Confluences (RSI 14 Momentum, EMA 50 & EMA 200 Trend Filter, Volume Spikes)
      - Average Price Range (APR / ATR 14 Volatility Bounds)
      - Support & Resistance Pivot Levels
    """

    @staticmethod
    def analyze_market(df: pd.DataFrame, timeframe: str = "1h") -> dict:
        if df.empty or len(df) < 30:
            return {"error": "Insufficient market data for SMC analysis"}

        df = df.copy()

        swings = SMCAnalyzer._find_swings(df, window=5)
        structure = SMCAnalyzer._detect_market_structure(df, swings)
        fvgs = SMCAnalyzer._detect_fvgs(df)
        order_blocks = SMCAnalyzer._detect_order_blocks(df, swings)
        liquidity = SMCAnalyzer._detect_liquidity_sweeps(df, swings)
        eq_data = SMCAnalyzer._calculate_premium_discount(df, swings)
        fib_data = SMCAnalyzer._calculate_fibonacci_levels(df, swings, structure["trend"])
        apr_data = SMCAnalyzer._calculate_apr_tool(df)
        indicators = SMCAnalyzer._calculate_technical_indicators(df)
        sr_levels = SMCAnalyzer._calculate_sr_levels(df)

        return {
            "timeframe": timeframe,
            "current_price": float(df["Close"].iloc[-1]),
            "structure": structure,
            "swings": swings,
            "fvgs": fvgs,
            "order_blocks": order_blocks,
            "liquidity": liquidity,
            "premium_discount": eq_data,
            "fibonacci": fib_data,
            "apr_tool": apr_data,
            "indicators": indicators,
            "sr_levels": sr_levels
        }

    @staticmethod
    def _calculate_technical_indicators(df: pd.DataFrame) -> dict:
        """Calculates RSI 14, EMA 50, EMA 200, and Volume Expansion."""
        close = df["Close"]
        volume = df["Volume"]

        # RSI 14
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = float(100 - (100 / (1 + rs)).iloc[-1])
        if np.isnan(rsi):
            rsi = 50.0

        # EMA 50 & EMA 200
        ema_50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1])
        ema_200 = float(close.ewm(span=200, adjust=False).mean().iloc[-1])

        current_price = float(close.iloc[-1])
        ema_trend = "BULLISH" if current_price > ema_200 else "BEARISH"

        # Volume Expansion
        avg_volume = volume.tail(20).mean()
        last_volume = volume.iloc[-1]
        volume_spike = bool(last_volume > avg_volume * 1.2)

        return {
            "rsi_14": round(rsi, 1),
            "rsi_status": "OVERSOLD (Bullish)" if rsi < 40 else ("OVERBOUGHT (Bearish)" if rsi > 60 else "NEUTRAL"),
            "ema_50": round(ema_50, 2),
            "ema_200": round(ema_200, 2),
            "ema_trend": ema_trend,
            "volume_spike": volume_spike
        }

    @staticmethod
    def _find_swings(df: pd.DataFrame, window: int = 5) -> dict:
        highs = df["High"].values
        lows = df["Low"].values
        
        swing_highs = []
        swing_lows = []

        for i in range(window, len(df) - window):
            if highs[i] == max(highs[i - window : i + window + 1]):
                swing_highs.append({"index": i, "timestamp": df.index[i], "price": float(highs[i])})
            if lows[i] == min(lows[i - window : i + window + 1]):
                swing_lows.append({"index": i, "timestamp": df.index[i], "price": float(lows[i])})

        last_swing_high = swing_highs[-1] if swing_highs else {"price": float(df["High"].max())}
        last_swing_low = swing_lows[-1] if swing_lows else {"price": float(df["Low"].min())}

        return {
            "all_highs": swing_highs,
            "all_lows": swing_lows,
            "last_high": last_swing_high,
            "last_low": last_swing_low
        }

    @staticmethod
    def _detect_market_structure(df: pd.DataFrame, swings: dict) -> dict:
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]

        highs = [sh["price"] for sh in swings["all_highs"][-3:]]
        lows = [sl["price"] for sl in swings["all_lows"][-3:]]

        trend = "BULLISH"
        bos_status = "NEUTRAL"
        choch_status = "NEUTRAL"

        if len(highs) >= 2 and len(lows) >= 2:
            if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                trend = "BULLISH"
            elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                trend = "BEARISH"
            else:
                trend = "RANGING / SIDEWAYS"

        recent_close = df["Close"].iloc[-5:]
        
        if (recent_close > last_high).any():
            bos_status = "BULLISH_BOS" if trend == "BULLISH" else "BULLISH_CHOCH"
            choch_status = bos_status

        if (recent_close < last_low).any():
            bos_status = "BEARISH_BOS" if trend == "BEARISH" else "BEARISH_CHOCH"
            choch_status = bos_status

        return {
            "trend": trend,
            "bos": bos_status,
            "choch": choch_status,
            "last_high": last_high,
            "last_low": last_low
        }

    @staticmethod
    def _detect_fvgs(df: pd.DataFrame) -> dict:
        bullish_fvgs = []
        bearish_fvgs = []
        
        highs = df["High"].values
        lows = df["Low"].values
        closes = df["Close"].values
        timestamps = df.index
        current_price = closes[-1]

        for i in range(2, len(df)):
            if lows[i] > highs[i - 2]:
                gap_bottom = highs[i - 2]
                gap_top = lows[i]
                gap_size = gap_top - gap_bottom
                if gap_size / current_price * 100 >= FVG_THRESHOLD_PERCENT:
                    is_mitigated = (df["Low"].iloc[i+1:] < gap_bottom).any() if i < len(df) - 1 else False
                    bullish_fvgs.append({
                        "top": float(gap_top), "bottom": float(gap_bottom),
                        "midpoint": float((gap_top + gap_bottom) / 2),
                        "size": float(gap_size), "timestamp": timestamps[i], "mitigated": is_mitigated
                    })

            if highs[i] < lows[i - 2]:
                gap_top = lows[i - 2]
                gap_bottom = highs[i]
                gap_size = gap_top - gap_bottom
                if gap_size / current_price * 100 >= FVG_THRESHOLD_PERCENT:
                    is_mitigated = (df["High"].iloc[i+1:] > gap_top).any() if i < len(df) - 1 else False
                    bearish_fvgs.append({
                        "top": float(gap_top), "bottom": float(gap_bottom),
                        "midpoint": float((gap_top + gap_bottom) / 2),
                        "size": float(gap_size), "timestamp": timestamps[i], "mitigated": is_mitigated
                    })

        active_bullish = [f for f in bullish_fvgs if not f["mitigated"] and f["top"] <= current_price * 1.01]
        active_bearish = [f for f in bearish_fvgs if not f["mitigated"] and f["bottom"] >= current_price * 0.99]

        return {
            "all_bullish": bullish_fvgs, "all_bearish": bearish_fvgs,
            "active_bullish": active_bullish[-2:] if active_bullish else [],
            "active_bearish": active_bearish[-2:] if active_bearish else []
        }

    @staticmethod
    def _detect_order_blocks(df: pd.DataFrame, swings: dict) -> dict:
        bullish_obs = []
        bearish_obs = []

        opens = df["Open"].values
        closes = df["Close"].values
        highs = df["High"].values
        lows = df["Low"].values
        timestamps = df.index

        for i in range(5, len(df) - 2):
            if closes[i] < opens[i]:
                if closes[i + 2] - closes[i] > 5.0:
                    bullish_obs.append({"top": float(highs[i]), "bottom": float(lows[i]), "midpoint": float((highs[i] + lows[i]) / 2), "timestamp": timestamps[i]})

            if closes[i] > opens[i]:
                if closes[i] - closes[i + 2] > 5.0:
                    bearish_obs.append({"top": float(highs[i]), "bottom": float(lows[i]), "midpoint": float((highs[i] + lows[i]) / 2), "timestamp": timestamps[i]})

        return {
            "bullish_ob": bullish_obs[-1] if bullish_obs else None,
            "bearish_ob": bearish_obs[-1] if bearish_obs else None,
            "all_bullish": bullish_obs[-3:],
            "all_bearish": bearish_obs[-3:]
        }

    @staticmethod
    def _detect_liquidity_sweeps(df: pd.DataFrame, swings: dict) -> dict:
        recent_candles = df.tail(10)
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]

        sweep_high = False
        sweep_low = False

        for _, row in recent_candles.iterrows():
            if row["High"] > last_high and row["Close"] < last_high:
                sweep_high = True
            if row["Low"] < last_low and row["Close"] > last_low:
                sweep_low = True

        return {"sweep_high": sweep_high, "sweep_low": sweep_low, "eqh_level": last_high, "eql_level": last_low}

    @staticmethod
    def _calculate_premium_discount(df: pd.DataFrame, swings: dict) -> dict:
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]
        current_price = df["Close"].iloc[-1]

        swing_range = max(last_high - last_low, 1.0)
        equilibrium = last_low + (swing_range * PREMIUM_DISCOUNT_EQUILIBRIUM)
        pct_position = (current_price - last_low) / swing_range * 100
        zone = "DISCOUNT" if current_price < equilibrium else "PREMIUM"

        return {
            "swing_high": last_high, "swing_low": last_low,
            "equilibrium_50pct": float(equilibrium),
            "current_price": float(current_price), "zone": zone,
            "position_percent": float(pct_position)
        }

    @staticmethod
    def _calculate_fibonacci_levels(df: pd.DataFrame, swings: dict, trend: str) -> dict:
        high = swings["last_high"]["price"]
        low = swings["last_low"]["price"]
        current_price = df["Close"].iloc[-1]

        rng = max(high - low, 1.0)

        if trend == "BULLISH":
            fib_618 = high - (rng * 0.618)
            fib_786 = high - (rng * 0.786)
        else:
            fib_618 = low + (rng * 0.618)
            fib_786 = low + (rng * 0.786)

        in_golden_pocket = (fib_786 <= current_price <= fib_618 * 1.002) if trend == "BULLISH" else (fib_618 * 0.998 <= current_price <= fib_786)

        return {
            "trend": trend,
            "fib_618": float(fib_618),
            "fib_786": float(fib_786),
            "in_golden_pocket": in_golden_pocket
        }

    @staticmethod
    def _calculate_apr_tool(df: pd.DataFrame, period: int = 14) -> dict:
        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = float(tr.rolling(period).mean().iloc[-1])
        current_price = float(close.iloc[-1])

        return {
            "atr_14": float(round(atr, 2)),
            "current_price": current_price,
            "expected_upper_bound": round(current_price + (atr * 1.5), 2),
            "expected_lower_bound": round(current_price - (atr * 1.5), 2)
        }

    @staticmethod
    def _calculate_sr_levels(df: pd.DataFrame) -> dict:
        recent = df.tail(50)
        pdh = float(recent["High"].max())
        pdl = float(recent["Low"].min())
        pivot = float((pdh + pdl + recent["Close"].iloc[-1]) / 3)

        return {
            "pdh": pdh, "pdl": pdl, "pivot": pivot,
            "r1": float((2 * pivot) - pdl), "s1": float((2 * pivot) - pdh)
        }

if __name__ == "__main__":
    from data_fetcher import DataFetcher
    print("Testing SMCAnalyzer with RSI, EMA & Volume Confluences...")
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    analysis = SMCAnalyzer.analyze_market(df_1h, timeframe="1h")
    print(f"RSI 14: {analysis['indicators']['rsi_14']} ({analysis['indicators']['rsi_status']})")
    print(f"EMA 200 Trend: {analysis['indicators']['ema_trend']}")
