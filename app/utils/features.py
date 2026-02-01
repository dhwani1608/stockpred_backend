import pandas as pd
import numpy as np
from typing import Dict


def calculate_features(ohlcv_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate technical features from OHLCV data.
    
    Expected DataFrame columns: Open, High, Low, Close, Volume
    """
    df = ohlcv_data.copy()
    
    # Returns
    close = df["Close"]
    return_1 = float(close.pct_change(1).iloc[-1]) if len(df) >= 2 else 0.0
    return_5 = float(close.pct_change(5).iloc[-1]) if len(df) >= 6 else 0.0
    
    # Moving averages
    ma_10 = float(close.rolling(10).mean().iloc[-1]) if len(df) >= 10 else close.iloc[-1]
    ma_20 = float(close.rolling(20).mean().iloc[-1]) if len(df) >= 20 else close.iloc[-1]
    
    # Exponential moving average
    ema_10 = float(close.ewm(span=10).mean().iloc[-1]) if len(df) >= 10 else close.iloc[-1]
    
    # Volatility
    returns = close.pct_change()
    volatility_10 = float(returns.rolling(10).std().iloc[-1]) if len(df) >= 10 else 0.01
    
    # Lag features
    lag_1 = float(close.iloc[-2]) if len(df) >= 2 else close.iloc[-1]
    lag_5 = float(close.iloc[-6]) if len(df) >= 6 else close.iloc[-1]
    
    # Current close
    current_close = float(close.iloc[-1])
    
    return {
        "Close": current_close,
        "Return_1": return_1,
        "Return_5": return_5,
        "MA_10": ma_10,
        "MA_20": ma_20,
        "EMA_10": ema_10,
        "Volatility_10": volatility_10,
        "Lag_1": lag_1,
        "Lag_5": lag_5,
    }
