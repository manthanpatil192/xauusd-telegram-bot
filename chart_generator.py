import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from pathlib import Path
from data_fetcher import DataFetcher
from smc_analyzer import SMCAnalyzer

class ChartGenerator:
    """
    Generates annotated dark-mode candlestick chart images for XAUUSD
    showing Entry, SL, TP levels, Order Blocks, FVGs, Fibonacci 61.8% Level, and Average Price Range (APR).
    """

    @staticmethod
    def generate_signal_chart(df: pd.DataFrame, signal_data: dict, output_path: str = "chart.png") -> str:
        if df.empty:
            df = DataFetcher.fetch_ohlcv(interval="1h")

        df = df.tail(40).copy()

        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
        fig.patch.set_facecolor("#12141D")
        ax.set_facecolor("#181B26")

        indexes = np.arange(len(df))
        opens = df["Open"].values
        highs = df["High"].values
        lows = df["Low"].values
        closes = df["Close"].values

        for i in range(len(df)):
            color = "#00E676" if closes[i] >= opens[i] else "#FF5252"
            ax.plot([indexes[i], indexes[i]], [lows[i], highs[i]], color=color, linewidth=1.2)
            body_bottom = min(opens[i], closes[i])
            body_top = max(opens[i], closes[i])
            body_height = max(body_top - body_bottom, 0.10)
            rect = plt.Rectangle((indexes[i] - 0.35, body_bottom), 0.7, body_height, facecolor=color, edgecolor=color, alpha=0.9)
            ax.add_patch(rect)

        entry = signal_data["entry"]
        sl = signal_data["sl"]
        tp1 = signal_data["tp1"]
        tp2 = signal_data["tp2"]

        ax.axhline(y=entry, color="#29B6F6", linestyle="--", linewidth=1.8, label=f"ENTRY: ${entry:.2f}")
        ax.axhline(y=sl, color="#FF1744", linestyle="-.", linewidth=1.8, label=f"STOP LOSS: ${sl:.2f}")
        ax.axhline(y=tp1, color="#00E676", linestyle=":", linewidth=1.8, label=f"TAKE PROFIT 1: ${tp1:.2f}")
        ax.axhline(y=tp2, color="#76FF03", linestyle="-", linewidth=2.0, label=f"TAKE PROFIT 2: ${tp2:.2f}")

        # Plot Trend-Based Fibonacci 61.8% Golden Ratio Line
        fib618 = signal_data.get("fib_618")
        if fib618:
            ax.axhline(y=fib618, color="#FFD700", linestyle="-", linewidth=1.5, alpha=0.85, label=f"Fib 61.8% Golden Ratio: ${fib618:.2f}")

        # Plot Average Price Range (APR) Bounds
        apr_upper = signal_data.get("apr_upper")
        apr_lower = signal_data.get("apr_lower")
        if apr_upper and apr_lower:
            ax.axhline(y=apr_upper, color="#AB47BC", linestyle=":", linewidth=1.2, alpha=0.7, label=f"APR Upper Range: ${apr_upper:.2f}")
            ax.axhline(y=apr_lower, color="#AB47BC", linestyle=":", linewidth=1.2, alpha=0.7, label=f"APR Lower Range: ${apr_lower:.2f}")

        # Highlight Order Blocks
        smc_1h = signal_data.get("raw_smc_1h", {})
        if "order_blocks" in smc_1h:
            bull_ob = smc_1h["order_blocks"].get("bullish_ob")
            if bull_ob:
                ax.axhspan(bull_ob["bottom"], bull_ob["top"], color="#00E676", alpha=0.15, label="Bullish Order Block")
            
            bear_ob = smc_1h["order_blocks"].get("bearish_ob")
            if bear_ob:
                ax.axhspan(bear_ob["bottom"], bear_ob["top"], color="#FF1744", alpha=0.15, label="Bearish Order Block")

        action = signal_data["action"]
        stars = signal_data["confidence_stars"]
        ax.set_title(f"XAUUSD (Gold) SMC & Fib 61.8% Setup | {action} {stars}", fontsize=14, fontweight="bold", pad=12, color="#FFFFFF")
        ax.set_ylabel("Price ($ USD)", fontsize=11, color="#B0BEC5")

        time_labels = [t.strftime("%H:%M") if hasattr(t, "strftime") else str(t) for t in df.index]
        step = max(len(df) // 6, 1)
        ax.set_xticks(indexes[::step])
        ax.set_xticklabels(time_labels[::step], color="#B0BEC5", rotation=25)

        ax.grid(True, color="#263238", linestyle=":", alpha=0.6)
        ax.legend(loc="upper left", facecolor="#1E2330", edgecolor="#37474F", fontsize=9, labelcolor="#FFFFFF")

        plt.tight_layout()

        out_file = Path(output_path).resolve()
        plt.savefig(out_file, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close()

        return str(out_file)

if __name__ == "__main__":
    from signal_generator import SignalGenerator
    print("Testing ChartGenerator with Fib 61.8% & APR visual annotations...")
    signal = SignalGenerator.generate_signal()
    df_1h = DataFetcher.fetch_ohlcv(interval="1h")
    file_path = ChartGenerator.generate_signal_chart(df_1h, signal, "test_fib_chart.png")
    print(f"Saved chart to: {file_path}")
