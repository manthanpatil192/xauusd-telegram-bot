import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from config import FVG_THRESHOLD_PERCENT, OB_SWING_LOOKBACK, PREMIUM_DISCOUNT_EQUILIBRIUM

class SMCAnalyzer:
    """
    Core Smart Money Concepts (SMC) & Inner Circle Trader (ICT) Analysis Engine.
    Includes:
      - Swing Highs & Swing Lows
      - Break of Structure (BOS) & Change of Character (CHOCH)
      - Fair Value Gaps (FVG)
      - Bullish & Bearish Order Blocks (OB)
      - Liquidity Sweeps (EQH / EQL Liquidity Grab)
      - Premium vs Discount 50% Equilibrium Zones
      - Trend-Based Fibonacci Retracement (61.8% Golden Pocket, 78.6%, 50%, 38.2%)
      - Average Price Range (APR / ATR Volatility Tool)
      - Support & Resistance (S/R) Pivot Levels
    """

    @staticmethod
    def analyze_market(df: pd.DataFrame, timeframe: str = "1h") -> dict:
        """
        Runs comprehensive SMC, ICT, Fibonacci & APR analysis on the provided DataFrame.
        """
        if df.empty or len(df) < 30:
            return {"error": "Insufficient market data for SMC analysis"}

        df = df.copy()

        # 1. Swing Highs & Lows
        swings = SMCAnalyzer._find_swings(df, window=5)
        
        # 2. Market Structure (BOS / CHOCH)
        structure = SMCAnalyzer._detect_market_structure(df, swings)
        
        # 3. Fair Value Gaps (FVG)
        fvgs = SMCAnalyzer._detect_fvgs(df)
        
        # 4. Order Blocks (OB)
        order_blocks = SMCAnalyzer._detect_order_blocks(df, swings)

        # 5. Liquidity Sweeps (EQH / EQL)
        liquidity = SMCAnalyzer._detect_liquidity_sweeps(df, swings)

        # 6. Premium vs Discount Zone
        eq_data = SMCAnalyzer._calculate_premium_discount(df, swings)

        # 7. Trend-Based Fibonacci Retracement Levels (61.8% Golden Pocket)
        fib_data = SMCAnalyzer._calculate_fibonacci_levels(df, swings, structure["trend"])

        # 8. Average Price Range (APR / ATR Volatility Tool)
        apr_data = SMCAnalyzer._calculate_apr_tool(df)

        # 9. Support & Resistance Pivot Levels
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
            "sr_levels": sr_levels
        }

    @staticmethod
    def _find_swings(df: pd.DataFrame, window: int = 5) -> dict:
        """Identifies Swing Highs and Swing Lows."""
        highs = df["High"].values
        lows = df["Low"].values
        
        swing_highs = []
        swing_lows = []

        for i in range(window, len(df) - window):
            if highs[i] == max(highs[i - window : i + window + 1]):
                swing_highs.append({
                    "index": i,
                    "timestamp": df.index[i],
                    "price": float(highs[i])
                })
            if lows[i] == min(lows[i - window : i + window + 1]):
                swing_lows.append({
                    "index": i,
                    "timestamp": df.index[i],
                    "price": float(lows[i])
                })

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
        """Detects Trend Direction, BOS (Break of Structure) & CHOCH (Change of Character)."""
        current_close = df["Close"].iloc[-1]
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
            if trend == "BULLISH":
                bos_status = "BULLISH_BOS"
            else:
                choch_status = "BULLISH_CHOCH"

        if (recent_close < last_low).any():
            if trend == "BEARISH":
                bos_status = "BEARISH_BOS"
            else:
                choch_status = "BEARISH_CHOCH"

        return {
            "trend": trend,
            "bos": bos_status,
            "choch": choch_status,
            "last_high": last_high,
            "last_low": last_low
        }

    @staticmethod
    def _detect_fvgs(df: pd.DataFrame) -> dict:
        """Detects Bullish & Bearish Fair Value Gaps (FVG)."""
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
                        "top": float(gap_top),
                        "bottom": float(gap_bottom),
                        "midpoint": float((gap_top + gap_bottom) / 2),
                        "size": float(gap_size),
                        "timestamp": timestamps[i],
                        "mitigated": is_mitigated
                    })

            if highs[i] < lows[i - 2]:
                gap_top = lows[i - 2]
                gap_bottom = highs[i]
                gap_size = gap_top - gap_bottom

                if gap_size / current_price * 100 >= FVG_THRESHOLD_PERCENT:
                    is_mitigated = (df["High"].iloc[i+1:] > gap_top).any() if i < len(df) - 1 else False
                    bearish_fvgs.append({
                        "top": float(gap_top),
                        "bottom": float(gap_bottom),
                        "midpoint": float((gap_top + gap_bottom) / 2),
                        "size": float(gap_size),
                        "timestamp": timestamps[i],
                        "mitigated": is_mitigated
                    })

        active_bullish = [f for f in bullish_fvgs if not f["mitigated"] and f["top"] <= current_price * 1.01]
        active_bearish = [f for f in bearish_fvgs if not f["mitigated"] and f["bottom"] >= current_price * 0.99]

        return {
            "all_bullish": bullish_fvgs,
            "all_bearish": bearish_fvgs,
            "active_bullish": active_bullish[-2:] if active_bullish else [],
            "active_bearish": active_bearish[-2:] if active_bearish else []
        }

    @staticmethod
    def _detect_order_blocks(df: pd.DataFrame, swings: dict) -> dict:
        """Detects Bullish & Bearish Institutional Order Blocks (OB)."""
        bullish_obs = []
        bearish_obs = []

        opens = df["Open"].values
        closes = df["Close"].values
        highs = df["High"].values
        lows = df["Low"].values
        timestamps = df.index

        for i in range(5, len(df) - 2):
            if closes[i] < opens[i]:  # Red candle
                future_move = closes[i + 2] - closes[i]
                if future_move > 5.0:
                    bullish_obs.append({
                        "top": float(highs[i]),
                        "bottom": float(lows[i]),
                        "midpoint": float((highs[i] + lows[i]) / 2),
                        "timestamp": timestamps[i],
                        "type": "Bullish OB"
                    })

            if closes[i] > opens[i]:  # Green candle
                future_move = closes[i] - closes[i + 2]
                if future_move > 5.0:
                    bearish_obs.append({
                        "top": float(highs[i]),
                        "bottom": float(lows[i]),
                        "midpoint": float((highs[i] + lows[i]) / 2),
                        "timestamp": timestamps[i],
                        "type": "Bearish OB"
                    })

        last_bullish_ob = bullish_obs[-1] if bullish_obs else None
        last_bearish_ob = bearish_obs[-1] if bearish_obs else None

        return {
            "bullish_ob": last_bullish_ob,
            "bearish_ob": last_bearish_ob,
            "all_bullish": bullish_obs[-3:],
            "all_bearish": bearish_obs[-3:]
        }

    @staticmethod
    def _detect_liquidity_sweeps(df: pd.DataFrame, swings: dict) -> dict:
        """Detects Liquidity Raids / Sweeps over EQH or EQL."""
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

        return {
            "sweep_high": sweep_high,
            "sweep_low": sweep_low,
            "eqh_level": last_high,
            "eql_level": last_low
        }

    @staticmethod
    def _calculate_premium_discount(df: pd.DataFrame, swings: dict) -> dict:
        """Calculates ICT Premium vs Discount Equilibrium (50% level of swing range)."""
        last_high = swings["last_high"]["price"]
        last_low = swings["last_low"]["price"]
        current_price = df["Close"].iloc[-1]

        swing_range = max(last_high - last_low, 1.0)
        equilibrium = last_low + (swing_range * PREMIUM_DISCOUNT_EQUILIBRIUM)
        pct_position = (current_price - last_low) / swing_range * 100

        zone = "DISCOUNT" if current_price < equilibrium else "PREMIUM"

        return {
            "swing_high": last_high,
            "swing_low": last_low,
            "equilibrium_50pct": float(equilibrium),
            "current_price": float(current_price),
            "zone": zone,
            "position_percent": float(pct_position)
        }

    @staticmethod
    def _calculate_fibonacci_levels(df: pd.DataFrame, swings: dict, trend: str) -> dict:
        """
        Calculates Trend-Based Fibonacci Retracement levels:
        - 23.6% (0.236)
        - 38.2% (0.382)
        - 50.0% (0.500 Equilibrium)
        - 61.8% (0.618 Golden Pocket / Golden Ratio)
        - 78.6% (0.786 Deep Retracement OTE)
        """
        high = swings["last_high"]["price"]
        low = swings["last_low"]["price"]
        current_price = df["Close"].iloc[-1]

        rng = max(high - low, 1.0)

        if trend == "BULLISH":
            # Retracement from High downwards
            fib_0 = high
            fib_236 = high - (rng * 0.236)
            fib_382 = high - (rng * 0.382)
            fib_500 = high - (rng * 0.500)
            fib_618 = high - (rng * 0.618)  # Golden Ratio 61.8%
            fib_786 = high - (rng * 0.786)  # Deep Retracement 78.6%
            fib_100 = low
        else:
            # Retracement from Low upwards
            fib_0 = low
            fib_236 = low + (rng * 0.236)
            fib_382 = low + (rng * 0.382)
            fib_500 = low + (rng * 0.500)
            fib_618 = low + (rng * 0.618)  # Golden Ratio 61.8%
            fib_786 = low + (rng * 0.786)  # Deep Retracement 78.6%
            fib_100 = high

        # Check if price is inside Golden Pocket Zone (61.8% to 78.6%)
        in_golden_pocket = False
        if trend == "BULLISH" and (fib_786 <= current_price <= fib_618 * 1.002):
            in_golden_pocket = True
        elif trend == "BEARISH" and (fib_618 * 0.998 <= current_price <= fib_786):
            in_golden_pocket = True

        return {
            "trend": trend,
            "fib_0": float(fib_0),
            "fib_236": float(fib_236),
            "fib_382": float(fib_382),
            "fib_500": float(fib_500),
            "fib_618": float(fib_618),  # Golden Ratio 61.8%
            "fib_786": float(fib_786),  # 78.6%
            "fib_100": float(fib_100),
            "in_golden_pocket": in_golden_pocket
        }

    @staticmethod
    def _calculate_apr_tool(df: pd.DataFrame, period: int = 14) -> dict:
        """
        Calculates Average Price Range (APR / ATR Volatility Tool)
        to measure average price movement, volatility bounds, and dynamic target projections.
        """
        df = df.copy()
        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        tr1 = high - low
        tr2 = (high - close.shift(1)).abs()
        tr3 = (low - close.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        atr = float(tr.rolling(period).mean().iloc[-1])
        current_price = float(close.iloc[-1])

        # Calculate Average Daily/Hourly Price Range expansion limits
        expected_high_range = round(current_price + (atr * 1.5), 2)
        expected_low_range = round(current_price - (atr * 1.5), 2)

        return {
            "atr_14": float(round(atr, 2)),
            "apr_percentage": float(round((atr / current_price) * 100, 2)),
            "current_price": current_price,
            "expected_upper_bound": expected_high_range,
            "expected_lower_bound": expected_low_range
        }

    @staticmethod
    def _calculate_sr_levels(df: pd.DataFrame) -> dict:
        """Calculates Pivot Support & Resistance key price zones."""
        recent = df.tail(50)
        pdh = float(recent["High"].max())
        pdl = float(recent["Low"].min())
        pivot = float((pdh + pdl + recent["Close"].iloc[-1]) / 3)

        r1 = float((2 * pivot) - pdl)
        s1 = float((2 * pivot) - pdh)
        r2 = float(pivot + (pdh - pdl))
        s2 = float(pivot - (pdh - pdl))

        return {
            "pdh": pdh,
            "pdl": pdl,
            "pivot": pivot,
            "r1": r1,
            "s1": s1,
            "r2": r2,
            "s2": s2
        }

if __name__ == "__main__":
    from data_fetcher import DataFetcher
    print("Testing SMCAnalyzer with Fibonacci 61.8% & APR Tool...")
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    analysis = SMCAnalyzer.analyze_market(df_1h, timeframe="1h")
    print(f"Current Gold Price: ${analysis['current_price']:.2f}")
    print(f"Fibonacci 61.8% Golden Ratio Level: ${analysis['fibonacci']['fib_618']:.2f}")
    print(f"Inside Golden Pocket: {analysis['fibonacci']['in_golden_pocket']}")
    print(f"14-period APR / ATR: ${analysis['apr_tool']['atr_14']:.2f}")
